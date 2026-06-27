"""Background job queue management for executions.

Provides queue management for security tool executions including job queuing,
dependency management, and result processing for background execution workflows.
"""

import rq
from django.utils import timezone
from django_rq import job
from rq.job import Job
from rq.registry import DeferredJobRegistry

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
    """Queue manager for security tool executions.

    Manages background execution of security tools using Redis Queue (RQ)
    with job queuing, dependency management, and result processing capabilities.

    Attributes:
        name (str): The name of the queue ('executions')
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
    ) -> Job:
        """Enqueue an execution job for background processing.

        Queues a security tool execution with all necessary parameters and
        dependencies for background processing.

        Args:
            execution (Execution): The execution instance to queue
            findings (list[Finding]): Findings to process
            target_ports (list[TargetPort]): Target ports to scan
            input_vulnerabilities (list[InputVulnerability]): Input vulnerabilities
            input_technologies (list[InputTechnology]): Input technologies
            wordlists (list[Wordlist]): Wordlists to use
            dependencies (list[Job]): Job dependencies for execution order
            at_front (bool): Whether to prioritize this job in the queue

        Returns:
            Job: The queued RQ job instance
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
        """Process an execution job.

        Main job consumer that executes security tools and processes results.
        Handles dependency resolution, tool execution, and result parsing.

        Args:
            execution (Execution): The execution instance to process
            findings (list[Finding]): Findings to process
            target_ports (list[TargetPort]): Target ports to scan
            input_vulnerabilities (list[InputVulnerability]): Input vulnerabilities
            input_technologies (list[InputTechnology]): Input technologies
            wordlists (list[Wordlist]): Wordlists to use

        Returns:
            tuple[Execution, list[Finding]]: Execution and resulting findings
        """
        BaseScanQueue.logger.info(
            f"[Execution] Execution {execution.id} ({execution.configuration.tool.name} - "
            f"{execution.configuration.name}) has started"
        )
        # Initialize the tool-specific executor for this execution
        executor: BaseExecutor = execution.configuration.tool.executor_class(execution)
        current_job = rq.get_current_job()
        # Handle dependency resolution for tool chaining workflows
        # If no findings provided but dependencies exist, extract findings from dependency results
        if not findings and current_job and current_job._dependency_ids:
            # Resolve findings from completed dependency jobs and create additional executions if needed
            # This enables automatic tool chaining where tool outputs become inputs for subsequent tools
            _execution = ExecutionsQueue._get_findings_from_dependencies(
                executor,
                target_ports,
                input_vulnerabilities,
                input_technologies,
                wordlists,
                current_job,
            )
            # Execute the tool with findings from dependencies
            executor.execute(
                _execution.findings,
                _execution.target_ports,
                _execution.input_vulnerabilities,
                _execution.input_technologies,
                _execution.wordlists,
            )
        else:
            # Execute the tool with provided findings (standard execution path)
            executor.execute(findings, target_ports, input_vulnerabilities, input_technologies, wordlists)
        # Parse the tool output to extract security findings
        parser: BaseParser = execution.configuration.tool.parser_class(executor, execution.output_plain)
        parser.parse()
        # Queue the extracted findings for background processing (alerts, integrations, etc.)
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
        """Get findings from job dependencies and create new executions.

        Processes job dependencies to extract findings and create new executions
        for tool chaining workflows based on dependency results.

        Args:
            executor (BaseExecutor): The executor instance
            target_ports (list[TargetPort]): Target ports
            input_vulnerabilities (list[InputVulnerability]): Input vulnerabilities
            input_technologies (list[InputTechnology]): Input technologies
            wordlists (list[Wordlist]): Wordlists
            current_job (Job): The current job being processed

        Returns:
            ExecutionParametersToEnqueue: Parameters for the next execution
        """
        findings = []
        self = ExecutionsQueue()
        # Extract findings from all dependency jobs to enable tool chaining
        # Each dependency job returns (execution, findings) tuple, so we take findings[1]
        for dependency_id in current_job._dependency_ids:
            dependency = self.queue.fetch_job(dependency_id)
            if dependency and dependency.result:
                findings.extend(dependency.result[1])
        # If no findings from dependencies, return only one execution with original parameters
        if not findings:
            return ExecutionParametersToEnqueue(
                findings, target_ports, input_vulnerabilities, input_technologies, wordlists
            )
        # Calculate new executions based on findings from dependencies
        # This enables automatic tool chaining where findings from one tool
        # trigger executions of other tools
        executions = [
            e
            for e in ExecutionsQueue.calculate_executions(
                executor.execution.configuration,
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
        BaseScanQueue.logger.info(f"[Execution] New {len(executions) - 1} executions from previous findings")
        # Create new execution records and queue jobs for additional executions
        # executions[0] is the current execution, executions[1:] are new ones
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
        # Update pending jobs that depend on current_job to include new dependencies
        # This ensures proper dependency chain for tool chaining workflows
        if new_jobs:
            registry = DeferredJobRegistry(queue=self.queue)
            for pending_job_id in registry.get_job_ids():
                pending_job = self.fetch_job(pending_job_id)
                if pending_job and current_job.id in pending_job._dependency_ids:
                    dependencies = pending_job._dependency_ids
                    meta = pending_job.get_meta()
                    # Cancel and recreate the pending job with updated dependencies
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
        # Return the first execution (current one) if available, otherwise fallback
        # to original parameters
        return (
            executions[0]
            if executions
            else ExecutionParametersToEnqueue(
                findings, target_ports, input_vulnerabilities, input_technologies, wordlists
            )
        )
