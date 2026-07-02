"""Background job processing infrastructure using Redis Queue (RQ).

Provides base classes and utilities for managing security tool executions
through background job queues with parameter calculation and batching.
"""

import copy
from dataclasses import dataclass
from functools import cached_property
from typing import Any

import django_rq
from rq.job import Job
from rq.queue import Queue

from findings.framework.models import Finding
from framework.logging import LoggingEntity
from framework.models import BaseInput
from input_types.models import InputType
from parameters.models import InputTechnology, InputVulnerability
from target_ports.models import TargetPort
from tools.models import Configuration, Input
from wordlists.models import Wordlist


@dataclass
class ExecutionParametersToEnqueue:
    """Data class for batching execution parameters before queuing.

    Organizes different types of input data that will be passed to
    security tool executions, enabling efficient batching and deduplication.

    Attributes:
        findings (list[Finding]): Security findings to use as input.
        target_ports (list[TargetPort]): Target ports for scanning.
        input_vulnerabilities (list[InputVulnerability]): Vulnerabilities provided by auditors.
        input_technologies (list[InputTechnology]): Technologies provided by auditors.
        wordlists (list[Wordlist]): Wordlists for brute force attacks.

    Example:
        ```python
        params = ExecutionParametersToEnqueue(
            findings=[host_finding],
            target_ports=[port_80, port_443],
            input_vulnerabilities=[],
            input_technologies=[],
            wordlists=[]
        )
        params.append("findings", new_finding)
        ```
    """

    findings: list[Finding]
    target_ports: list[TargetPort]
    input_vulnerabilities: list[InputVulnerability]
    input_technologies: list[InputTechnology]
    wordlists: list[Wordlist]

    def append(self, field: str, value: BaseInput) -> None:
        """Append a single value to the specified field list.

        Args:
            field (str): The field name to append to.
            value (BaseInput): The value to append.
        """
        setattr(self, field, getattr(self, field) + [value])

    def extend(self, field: str, values: list[BaseInput]) -> None:
        """Extend the specified field list with multiple values.

        Args:
            field (str): The field name to extend.
            values (list[BaseInput]): The values to extend with.
        """
        setattr(self, field, getattr(self, field) + values)

    def __eq__(self, other: Any) -> bool:
        """Check equality with another ExecutionParametersToEnqueue instance.

        Args:
            other (Any): The other object to compare with.

        Returns:
            bool: True if all fields are equal, False otherwise.
        """
        if not isinstance(other, ExecutionParametersToEnqueue):
            return False
        return (
            self.findings == other.findings
            and self.target_ports == other.target_ports
            and self.input_vulnerabilities == other.input_vulnerabilities
            and self.input_technologies == other.input_technologies
            and self.wordlists == other.wordlists
        )

    def __hash__(self) -> int:
        """Generate hash for deduplication in sets and dictionaries.

        Returns:
            int: Hash value based on all field contents.
        """
        return hash(
            (
                tuple(self.findings),
                tuple(self.target_ports),
                tuple(self.input_vulnerabilities),
                tuple(self.input_technologies),
                tuple(self.wordlists),
            )
        )


class BaseQueue(LoggingEntity):
    """Base class for Redis Queue (RQ) job management.

    Provides common functionality for managing background jobs including
    job lifecycle management with basic queue operations like enqueueing,
    cancellation, and deletion.

    Attributes:
        name (str): The queue name for this job type.
    """

    name = ""

    @cached_property
    def queue(self) -> Queue:
        """Get the Redis Queue instance for this queue.

        Returns:
            Queue: The RQ Queue instance.
        """
        return django_rq.get_queue(self.name)

    def fetch_job(self, job_id: str) -> Job | None:
        """Fetch a job by ID from the queue.

        Args:
            job_id (str): The job ID to fetch.

        Returns:
            Job | None: The job instance or None if not found.
        """
        try:
            return self.queue.fetch_job(job_id)
        except Exception:
            return None

    def cancel_job(self, job_id: str) -> None:
        """Cancel a job by ID.

        Args:
            job_id (str): The job ID to cancel.
        """
        job = self.fetch_job(job_id)
        if job:
            self.logger.info(f"[{self.name}] Job {job_id} has been cancelled")
            job.cancel()

    def delete_job(self, job_id: str) -> None:
        """Delete a job by ID.

        Args:
            job_id (str): The job ID to delete.
        """
        job = self.fetch_job(job_id)
        if job:
            self.logger.info(f"[{self.name}] Job {job_id} has been deleted")
            job.delete()

    def enqueue(self, *args: Any, **kwargs: Any) -> Job:
        """Enqueue a job for background processing.

        Args:
            *args (Any): Arguments to pass to the consume method.
            **kwargs (Any): Keyword arguments including job options.

        Returns:
            Job: The enqueued job instance.
        """
        return self.queue.enqueue(self.consume, *args, **kwargs)

    @staticmethod
    def consume(**kwargs: Any) -> Any:
        """Process a job from the queue (implementation specific).

        Args:
            **kwargs (Any): Job parameters.

        Returns:
            Any: Job result.

        Note:
            This method should be overridden by concrete implementations.
        """
        pass


class BaseScanQueue(BaseQueue):
    """Base class for security scan queues with execution parameter calculation.

    Extends BaseQueue with specialized functionality for security tool executions
    including parameter calculation, input batching, and finding-based optimization.
    Used for queues that need to process security scanning operations.

    Execution Optimization:
        - Finding-based input type grouping and prioritization
        - Tool argument constraint analysis and batching
        - Input type dependency resolution and relationship handling
        - Multi-value argument optimization for efficient execution

    Attributes:
        Inherits all attributes from BaseQueue.
    """

    @staticmethod
    def _get_findings_by_type(
        findings: list[Finding],
    ) -> dict[InputType, list[Finding]]:
        """Group findings by their input type for processing efficiency.

        Args:
            findings (list[Finding]): List of findings to group.

        Returns:
            dict[InputType, list[Finding]]: Findings grouped by input type,
                                          sorted by dependency complexity.
        """
        findings_by_type = {}
        for finding in findings:
            if finding.input_type not in findings_by_type:
                findings_by_type[finding.input_type] = [finding]
            else:
                findings_by_type[finding.input_type].append(finding)
        # Sort findings by the input type ID to process the main findings first
        # So in calculate_executions, Hosts will be planned first, then their Ports, then their Paths, etc.
        return dict(sorted(findings_by_type.items(), key=lambda i: i[0].id))

    @staticmethod
    def calculate_executions(
        configuration: Configuration,
        findings: list[Finding],
        target_ports: list[TargetPort],
        input_vulnerabilities: list[InputVulnerability],
        input_technologies: list[InputTechnology],
        wordlists: list[Wordlist],
    ) -> list[ExecutionParametersToEnqueue]:
        """Calculate execution parameter batches for a tool.

        Analyzes tool input requirements and available data to create
        optimal execution batches that maximize efficiency while respecting
        tool argument constraints and dependencies.

        Args:
            configuration (Configuration): The security configuration to execute.
            findings (list[Finding]): Available findings for input.
            target_ports (list[TargetPort]): Available target ports.
            input_vulnerabilities (list[InputVulnerability]): Known vulnerabilities.
            input_technologies (list[InputTechnology]): Detected technologies.
            wordlists (list[Wordlist]): Available wordlists.

        Returns:
            list[ExecutionParametersToEnqueue]: Optimized parameter batches for execution.

        Note:
            The algorithm considers:
            - Tool input type requirements and filters
            - Argument multiplicity (single vs multiple values)
            - Input type dependencies and relationships
            - Execution optimization through intelligent batching
        """
        input_types_used = set()
        # Start with a single empty execution batch
        executions = [ExecutionParametersToEnqueue([], [], [], [], [])]
        findings_by_type = BaseScanQueue._get_findings_by_type(findings)
        # Iterate over all input sources (findings, ports, vulnerabilities, etc.)
        for field, source in [("findings", _findings) for _findings in findings_by_type.values()] + [
            ("target_ports", target_ports),
            ("input_vulnerabilities", input_vulnerabilities),
            ("input_technologies", input_technologies),
            ("wordlists", wordlists),
        ]:
            if not source:
                continue
            input_type = source[0].input_type
            # Avoid processing the same input type more than once
            if input_type in input_types_used:
                continue
            # For each configuration input that matches the input type, ordered by priority order
            for tool_input in Input.objects.filter(argument__configuration=configuration, type=input_type).order_by(
                "order"
            ):
                # Filter base inputs according to the tool input's filter logic
                filtered_base_inputs = [bi for bi in source if bi.filter(tool_input)]
                if not filtered_base_inputs:
                    continue
                # Find related input types (dependencies) for this input type
                parent_input_types = [i for i in input_type.parent_input_types if i in findings_by_type]
                for execution_index, execution in enumerate(copy.deepcopy(executions)):
                    # If this is a finding and has related input types, only include those related to the current execution
                    if field == "findings" and parent_input_types:
                        base_inputs = []
                        for parent_input_type in parent_input_types:
                            base_inputs.extend(
                                bi
                                for bi in filtered_base_inputs
                                if getattr(bi, parent_input_type.name.lower()) in execution.findings
                                and bi not in base_inputs
                            )
                        if not base_inputs:
                            continue
                    else:
                        base_inputs = list(set(filtered_base_inputs))
                    input_types_used.add(input_type)
                    # If the tool argument allows multiple values, extend the execution batch
                    if tool_input.argument.multiple:
                        executions[execution_index].extend(field, base_inputs)
                    else:
                        # For single-value arguments, create a new execution batch for each additional value
                        original_execution = copy.deepcopy(execution)
                        executions[execution_index].append(field, base_inputs[0])
                        for base_input in base_inputs[1:]:
                            executions.append(copy.deepcopy(original_execution))
                            executions[-1].append(field, base_input)
                break  # One valid input type is enough
        return executions
