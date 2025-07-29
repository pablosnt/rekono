import rq
from django.utils import timezone
from django_rq import job
from rq.job import Job
from rq.registry import DeferredJobRegistry

from executions.models import Execution
from findings.framework.models import Finding
from findings.queues import FindingsQueue
from framework.queues import BaseQueue, ExecutionParametersToEnqueue
from parameters.models import InputTechnology, InputVulnerability
from target_ports.models import TargetPort
from tools.executors.base import BaseExecutor
from tools.parsers.base import BaseParser
from wordlists.models import Wordlist


class ExecutionsQueue(BaseQueue):
    name = "executions"

    def enqueue(
        self,
        execution: Execution,
        findings: list[Finding],
        target_ports: list[TargetPort],
        input_vulnerabilities: list[InputVulnerability],
        input_technologies: list[InputTechnology],
        wordlists: list[Wordlist],
        dependencies: list[Job] = [],
        at_front: bool = False,
    ) -> Job:
        job = self.queue.enqueue(
            self.consume,
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
        self.logger.info(
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

    @staticmethod
    @job("executions")
    def consume(
        execution: Execution,
        findings: list[Finding],
        target_ports: list[TargetPort],
        input_vulnerabilities: list[InputVulnerability],
        input_technologies: list[InputTechnology],
        wordlists: list[Wordlist],
    ) -> tuple[Execution, list[Finding]]:
        executor: BaseExecutor = execution.configuration.tool.get_executor_class()(execution)
        current_job = rq.get_current_job()
        if not findings and current_job and current_job._dependency_ids:
            _execution = ExecutionsQueue._get_findings_from_dependencies(
                executor,
                target_ports,
                input_vulnerabilities,
                input_technologies,
                wordlists,
                current_job,
            )
            findings = _execution.findings
            target_ports = _execution.target_ports
            input_vulnerabilities = _execution.input_vulnerabilities
            input_technologies = _execution.input_technologies
            wordlists = _execution.wordlists
        executor.execute(_execution.findings, target_ports, input_vulnerabilities, input_technologies, wordlists)
        parser: BaseParser = execution.configuration.tool.get_parser_class()(executor, execution.output_plain)
        parser.parse()
        FindingsQueue().enqueue(execution, parser.findings)
        return execution, parser.findings

    @staticmethod
    def _get_findings_from_dependencies(
        executor: BaseExecutor,
        target_ports: list[TargetPort],
        input_vulnerabilities: list[InputVulnerability],
        input_technologies: list[InputTechnology],
        wordlists: list[Wordlist],
        current_job: Job,
    ) -> ExecutionParametersToEnqueue:
        findings = []
        self = ExecutionsQueue()
        for dependency_id in current_job._dependency_ids:
            dependency = self.queue.fetch_job(dependency_id)
            if dependency and dependency.result:
                findings.extend(dependency.result[1])
        if not findings:
            return ExecutionParametersToEnqueue(
                findings, target_ports, input_vulnerabilities, input_technologies, wordlists
            )
        executions = [
            e
            for e in ExecutionsQueue.calculate_executions(
                executor.execution.configuration.tool,
                findings,
                target_ports,
                input_vulnerabilities,
                input_technologies,
                wordlists,
            )
            if executor.check_arguments(
                e.findings, e.target_ports, e.input_vulnerabilities, e.input_technologies, e.wordlists
            )
        ]
        BaseQueue.logger.info(f"[Execution] New {len(executions) - 1} executions from previous findings")
        new_jobs = []
        for execution in executions[1:]:
            new_execution = Execution.objects.create(
                task=executor.execution.task,
                configuration=executor.execution.configuration,
            )
            job = self.enqueue(
                new_execution,
                execution.findings,
                execution.target_ports,
                execution.input_vulnerabilities,
                execution.input_technologies,
                execution.wordlists,
                # At queue start, because it could be a dependency of next jobs
                at_front=True,
            )
            new_jobs.append(job.id)
        if new_jobs:
            registry = DeferredJobRegistry(queue=self.queue)
            for pending_job_id in registry.get_job_ids():
                pending_job = self.fetch_job(pending_job_id)
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
        return (
            executions[0]
            if executions
            else ExecutionParametersToEnqueue(
                findings, target_ports, input_vulnerabilities, input_technologies, wordlists
            )
        )
