import logging
from typing import Dict, List, Tuple

import rq
from django.utils import timezone
from django_rq import job
from executions.models import Execution
from findings.framework.models import Finding
from findings.queues import FindingsQueue
from framework.models import BaseInput
from framework.queues import BaseQueue
from parameters.models import InputTechnology, InputVulnerability
from rq.job import Job
from rq.registry import DeferredJobRegistry
from target_ports.models import TargetPort
from tools.executors.base import BaseExecutor
from tools.models import Input, Tool
from tools.parsers.base import BaseParser
from wordlists.models import Wordlist

logger = logging.getLogger()


class ExecutionsQueue(BaseQueue):
    def __init__(self) -> None:
        super().__init__("executions-queue")
        self.findings_queue = FindingsQueue()

    def enqueue(
        self,
        execution: Execution,
        findings: List[Finding],
        target_ports: List[TargetPort],
        input_vulnerabilities: List[InputVulnerability],
        input_technologies: List[InputTechnology],
        wordlists: List[Wordlist],
        dependencies: List[Job] = [],
        at_front: bool = False,
    ) -> Job:
        job = self.queue.enqueue(
            self.consume.__func__,
            execution=execution,
            findings=findings,
            target_ports=target_ports,
            input_vulnerabilities=input_vulnerabilities,
            input_technologies=input_technologies,
            wordlists=wordlists,
            result_ttl=7200,
            depends_on=dependencies,
            at_front=at_front,
        )
        logger.info(
            f"[Execution] Execution {execution.id} ({execution.configuration.tool.name} - "
            f"{execution.configuration.name}) has been enqueued"
        )
        job.meta["execution"] = execution
        job.meta["target_ports"] = target_ports
        job.meta["input_vulnerabilities"] = input_vulnerabilities
        job.meta["input_technologies"] = input_technologies
        job.meta["wordlists"] = wordlists
        execution.enqueued_at = timezone.now()
        execution.rq_job_id = job.id
        execution.save(update_fields=["rq_job_id"])
        return job

    @job("executions-queue")
    def consume(
        self,
        execution: Execution,
        findings: List[Finding],
        target_ports: List[TargetPort],
        input_vulnerabilities: List[InputVulnerability],
        input_technologies: List[InputTechnology],
        wordlists: List[Wordlist],
    ) -> Tuple[Execution, List[Finding]]:
        executor: BaseExecutor = execution.configuration.tool.get_executor_class()(
            execution
        )
        current_job = rq.get_current_job()
        if not findings and current_job._dependency_ids:
            (
                findings,
                target_ports,
                input_vulnerabilities,
                input_technologies,
                wordlists,
            ) = self._get_findings_from_dependencies(
                executor,
                target_ports,
                input_vulnerabilities,
                input_technologies,
                wordlists,
            ).values()
        executor.execute(
            findings, target_ports, input_vulnerabilities, input_technologies, wordlists
        )
        parser: BaseParser = execution.configuration.tool.get_parser_class()(
            executor, execution.output_plain
        )
        parser.parse()
        self.findings_queue.enqueue(execution, parser.findings)
        return execution, parser.findings

    def _get_findings_from_dependencies(
        self,
        executor: BaseExecutor,
        target_ports: List[TargetPort],
        input_vulnerabilities: List[InputVulnerability],
        input_technologies: List[InputTechnology],
        wordlists: List[Wordlist],
        current_job: Job,
    ) -> Dict[int, List[BaseInput]]:
        findings = []
        for dependency_id in current_job._dependency_ids:
            dependency = self.queue.fetch_job(dependency_id)
            if dependency and dependency.result:
                findings.extend(dependency.result[1])
        if not findings:
            return findings
        executions = [
            e
            for e in self._calculate_executions(
                executor.execution.configuration.tool,
                findings,
                target_ports,
                input_vulnerabilities,
                input_technologies,
                wordlists,
            )
            if executor.check_arguments(
                e.get(0, []), e.get(1, []), e.get(2, []), e.get(3, []), e.get(4, [])
            )
        ]
        logger.info(
            f"[Execution] New {len(executions) - 1} executions from previous findings"
        )
        new_jobs = []
        for execution in executions[1:]:
            new_execution = Execution.objects.create(
                task=executor.execution.task,
                configuration=executor.execution.configuration,
                group=executor.execution.group,
            )
            job = self.enqueue(
                new_execution,
                execution.get(0, []),
                execution.get(1, []),
                execution.get(2, []),
                execution.get(3, []),
                execution.get(4, []),
                # At queue start, because it could be a dependency of next jobs
                at_front=True,
            )
            new_jobs.append(job.id)
        if new_jobs:
            registry = DeferredJobRegistry(queue=self.queue)
            for pending_job_id in registry.get_job_ids():
                pending_job = self.queue.fetch_job(pending_job_id)
                if pending_job and current_job.id in pending_job._dependency_ids:
                    dependencies = pending_job._dependency_ids
                    meta = pending_job.get_meta()
                    self.cancel_job(pending_job_id)
                    self.delete_job(pending_job_id)
                    self.enqueue(
                        meta["execution"],
                        [],
                        meta["target_ports"],
                        meta["input_vulnerabilities"],
                        meta["input_technologies"],
                        meta["wordlists"],
                        dependencies=dependencies + new_jobs,
                    )
        return executions[0] if executions else {}
