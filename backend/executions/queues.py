"""Queue that runs the tool executions and parses their output.

The findings that an execution reports become the input of the executions that
depend on it, so this queue also plans the new executions that those findings
require, and rewires the jobs that are still waiting.
"""

from typing import Any

import rq
from django.utils import timezone
from django_rq import job
from rq.job import Dependency, Job
from rq.registry import DeferredJobRegistry

from executions.enums import Status
from executions.models import Execution
from findings.framework.models import Finding
from findings.queues import FindingsQueue
from framework.queues import BaseScanQueue, ExecutionParametersToEnqueue
from parameters.models import InputTechnology, InputVulnerability
from target_ports.models import TargetPort
from tools.executors.base import BaseExecutor
from tools.parsers.base import BaseParser
from wordlists.models import Wordlist


class ExecutionsQueue(BaseScanQueue):
    """Queue that executes the tools and processes their findings.

    Attributes:
        name: Name of the RQ queue.
    """

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
        job_id: str | None = None,
    ) -> Job:
        """Enqueue an execution with the inputs that the tool will receive.

        Dependencies are wired with allow_failure=True so a dependent execution
        still runs when a dependency fails, treating its input as optional rather
        than being orphaned as stuck.

        Args:
            execution: Execution to be enqueued.
            findings: Findings from previous executions used as input.
            target_ports: Target ports of the scope of the task.
            input_vulnerabilities: Vulnerabilities provided by the auditor.
            input_technologies: Technologies provided by the auditor.
            wordlists: Wordlists selected for the task.
            dependencies: Jobs that must finish before this execution starts.
            at_front: Whether to enqueue this execution before the ones that are
                already waiting.
            job_id: Reuse this RQ job id instead of generating a new one.
                Used when recreating a pending job to add dependencies, so jobs that
                already depend on it keep pointing at a valid id.

        Returns:
            The enqueued job, whose metadata keeps the inputs so the job can be
            recreated later with new dependencies.
        """
        job = self.queue.enqueue(
            self.consume,
            execution=execution,
            findings=findings,
            target_ports=target_ports,
            input_vulnerabilities=input_vulnerabilities,
            input_technologies=input_technologies,
            wordlists=wordlists,
            result_ttl=7200,
            depends_on=Dependency(jobs=dependencies, allow_failure=True) if dependencies else [],
            at_front=at_front,
            job_id=job_id,
            on_failure=ExecutionsQueue.on_execution_failure,
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
        job.save_meta()
        execution.enqueued_at = timezone.now()
        execution.rq_job_id = job.id
        execution.save(update_fields=["rq_job_id", "enqueued_at"])
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
        """Execute one tool and parse the findings from its output.

        When the execution has dependencies and no findings of its own, the
        findings reported by those dependencies are collected first, since they are
        the input that this execution was waiting for.

        Args:
            execution: Execution to run, as it was when the job was enqueued.
            findings: Findings from previous executions used as input. Empty when
                the execution waits for dependencies, since their findings are only
                available once those jobs have finished.
            target_ports: Target ports of the scope of the task.
            input_vulnerabilities: Vulnerabilities provided by the auditor.
            input_technologies: Technologies provided by the auditor.
            wordlists: Wordlists selected for the task.

        Returns:
            The execution and the findings that it reported, which are what the
            executions depending on this one will receive. A skipped or cancelled
            execution reports no findings, since there is no output to parse.
        """
        BaseScanQueue.logger.info(
            f"[Execution] Execution {execution.id} ({execution.configuration.tool.name} - "
            f"{execution.configuration.name}) has started"
        )
        executor: BaseExecutor = execution.configuration.tool.executor_class(execution)
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
            executor.execute(
                _execution.findings,
                _execution.target_ports,
                _execution.input_vulnerabilities,
                _execution.input_technologies,
                _execution.wordlists,
            )
        else:
            executor.execute(findings, target_ports, input_vulnerabilities, input_technologies, wordlists)
        # A skipped or cancelled execution has no output and no built arguments to parse, so parsing
        # would fail. The status is refreshed because cancellations are applied to the execution
        # directly in the database from the task cancellation endpoint, and would otherwise be missed.
        execution.refresh_from_db(fields=["status"])
        if execution.status in [Status.SKIPPED, Status.CANCELLED]:
            return execution, []
        parser: BaseParser = execution.configuration.tool.parser_class(executor, execution.output_plain)
        parser.parse()
        # Successful executions must be completed after parsing their findings
        if execution.status == Status.RUNNING:
            execution.completed(executor.hash)
        FindingsQueue().enqueue(execution, parser.findings)
        return execution, parser.findings

    @staticmethod
    def on_execution_failure(job: Job, connection: Any, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        """Mark the execution as ERROR when its RQ job fails or is abandoned.

        RQ invokes this callback when the execution job raises an unhandled exception or is moved
        to the failed registry after being abandoned, so the execution is not left stuck in a
        pending status. Executions that already reached a terminal status are left untouched.

        Args:
            job: Failed job, whose kwargs keep the execution to be marked as errored.
            connection: Redis connection of the queue that ran the job.
            exc_type: Class of the unhandled exception, or AbandonedJobError when the job was
                abandoned instead of failing on its own.
            exc_value: Instance of the exception described by exc_type.
            traceback: Traceback of the unhandled exception, or the stack summary of the
                registry cleanup for an abandoned job.
        """
        execution = job.kwargs.get("execution")
        if not execution:
            return
        try:
            execution.refresh_from_db()
        except Execution.DoesNotExist:
            return
        if execution.status in Status.in_progress():
            execution.error()

    @staticmethod
    def _get_findings_from_dependencies(
        executor: BaseExecutor,
        target_ports: list[TargetPort],
        input_vulnerabilities: list[InputVulnerability],
        input_technologies: list[InputTechnology],
        wordlists: list[Wordlist],
        current_job: Job,
    ) -> ExecutionParametersToEnqueue:
        """Collect the findings reported by the dependencies of an execution.

        Those findings can need more executions than the one that is running, so
        the extra ones are created and enqueued here, and the jobs that were
        waiting for this one are recreated to wait for them too. The execution
        graph is recreated under a per-task lock so concurrent dependency jobs
        don't race while rewiring pending jobs with the new dependencies.

        Args:
            executor: Executor of the execution that is running.
            target_ports: Target ports of the scope of the task.
            input_vulnerabilities: Vulnerabilities provided by the auditor.
            input_technologies: Technologies provided by the auditor.
            wordlists: Wordlists selected for the task.
            current_job: Job of the execution that is running.

        Returns:
            The inputs that the current execution must use. The other batches of
            inputs are enqueued as new executions instead of being returned.
        """
        findings = []
        self = ExecutionsQueue()
        # Each dependency job returns an (execution, findings) tuple
        for dependency_id in current_job._dependency_ids:
            dependency = self.queue.fetch_job(dependency_id)
            if not dependency:
                BaseScanQueue.logger.info(
                    f"[Execution] Execution {executor.execution.id} received no result from not found dependency job {dependency_id}"
                )
            elif dependency.result:
                findings.extend(dependency.result[1])
                BaseScanQueue.logger.info(
                    f"[Execution] Execution {executor.execution.id} received {len(dependency.result[1])} findings of type {', '.join(sorted({f.__class__.__name__ for f in dependency.result[1]}))} from dependency job {dependency_id}"
                )
            else:
                BaseScanQueue.logger.info(
                    f"[Execution] Execution {executor.execution.id} received empty result from dependency job {dependency_id}"
                )
        BaseScanQueue.logger.info(
            f"[Execution] Execution {executor.execution.id} collected {len(findings)} findings of type {', '.join(sorted({f.__class__.__name__ for f in findings}))} from {len(current_job._dependency_ids)} dependencies"
        )
        if not findings:
            return ExecutionParametersToEnqueue(
                findings, target_ports, input_vulnerabilities, input_technologies, wordlists
            )
        executions = []
        for e in ExecutionsQueue.calculate_executions(
            executor.execution.configuration,
            findings,
            target_ports,
            input_vulnerabilities,
            input_technologies,
            wordlists,
        ):
            if executor.check_arguments(
                e.findings, e.target_ports, e.input_vulnerabilities, e.input_technologies, e.wordlists
            ):
                executions.append(e)
            else:
                BaseScanQueue.logger.info(
                    f"[Execution] Execution {executor.execution.id} discarded a parameter batch ({len(e.findings)} findings of type {', '.join(sorted({f.__class__.__name__ for f in e.findings}))}, {len(e.target_ports)} target ports, {len(e.input_vulnerabilities)} input vulnerabilities, {len(e.input_technologies)} input technologies, and {len(e.wordlists)} wordlists) that can't satisfy the required arguments"
                )
        BaseScanQueue.logger.info(f"[Execution] New {len(executions) - 1} executions from previous findings")
        # Lock RQ to recalculate the execution graph based on the latest results and the dependencies between jobs
        with self.queue.connection.lock(f"execution-graph:{executor.execution.task.id}"):
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
                        meta = pending_job.get_meta()
                        # Only execution jobs carry an "execution" in their meta and can be recreated
                        if "execution" not in meta:
                            continue
                        dependencies = pending_job._dependency_ids
                        self.delete_job(pending_job_id)
                        self.enqueue(
                            meta["execution"],
                            [],
                            meta["target_ports"],
                            meta["input_vulnerabilities"],
                            meta["input_technologies"],
                            meta["wordlists"],
                            dependencies=dependencies + new_jobs,
                            # Preserve previous job ID to avoid disruptions on dependencies
                            job_id=pending_job_id,
                        )
        return (
            executions[0]
            if executions
            else ExecutionParametersToEnqueue(
                findings, target_ports, input_vulnerabilities, input_technologies, wordlists
            )
        )
