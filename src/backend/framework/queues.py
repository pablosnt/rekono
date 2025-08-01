"""This module provides queue management and task scheduling utilities."""

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
from tools.models import Input, Tool
from wordlists.models import Wordlist


@dataclass
class ExecutionParametersToEnqueue:
    """Data class for organizing execution parameters to be enqueued.

    This class holds collections of different input types that will be
    processed together in a job execution.

    Attributes:
        findings: List of findings to process.
        target_ports: List of target ports to process.
        input_vulnerabilities: List of input vulnerabilities to process.
        input_technologies: List of input technologies to process.
        wordlists: List of wordlists to process.
    """

    findings: list[Finding] = []
    target_ports: list[TargetPort] = []
    input_vulnerabilities: list[InputVulnerability] = []
    input_technologies: list[InputTechnology] = []
    wordlists: list[Wordlist] = []

    def append(self, field: str, value: BaseInput) -> None:
        """Append a single value to a specific field.

        Args:
            field: The field name to append to.
            value: The value to append.
        """
        setattr(self, field, getattr(self, field) + [value])

    def extend(self, field: str, values: list[BaseInput]) -> None:
        """Extend a field with multiple values.

        Args:
            field: The field name to extend.
            values: List of values to add.
        """
        setattr(self, field, getattr(self, field) + values)

    def __eq__(self, other: Any) -> bool:
        """Check equality with another ExecutionParametersToEnqueue instance.

        Args:
            other: The object to compare with.

        Returns:
            True if all fields are equal, False otherwise.
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
        """Generate hash for this instance.

        Returns:
            Hash value based on all field contents.
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
    """Base class for queue management and job execution.

    This abstract base class provides functionality for managing RQ queues,
    enqueueing jobs, and processing execution parameters. It includes
    methods for job lifecycle management and execution calculation.

    Attributes:
        name (str): The name of the queue to use.
    """

    name = ""

    @cached_property
    def queue(self) -> Queue:
        """Get the RQ queue instance.

        Returns:
            The RQ Queue instance for this queue name.
        """
        return django_rq.get_queue(self.name)

    def fetch_job(self, job_id: str) -> Job | None:
        """Fetch a job by its ID.

        Args:
            job_id: The unique identifier of the job.

        Returns:
            The Job instance if found, None otherwise.
        """
        try:
            return self.queue.fetch_job(job_id)
        except Exception:
            return None

    def cancel_job(self, job_id: str) -> None:
        """Cancel a running job.

        Args:
            job_id: The unique identifier of the job to cancel.
        """
        job = self.fetch_job(job_id)
        if job:
            self.logger.info(f"[{self.name}] Job {job_id} has been cancelled")
            job.cancel()

    def delete_job(self, job_id: str) -> None:
        """Delete a job from the queue.

        Args:
            job_id: The unique identifier of the job to delete.
        """
        job = self.fetch_job(job_id)
        if job:
            self.logger.info(f"[{self.name}] Job {job_id} has been deleted")
            job.delete()

    def enqueue(self, *args: Any, **kwargs: Any) -> Job:
        """Enqueue a job for execution.

        Args:
            *args: Positional arguments for the job.
            **kwargs: Keyword arguments for the job.

        Returns:
            The enqueued Job instance.
        """
        return self.queue.enqueue(self.consume, *args, **kwargs)

    @staticmethod
    def consume(**kwargs: Any) -> Any:
        """Consume method to be implemented by subclasses.

        This method should be overridden by subclasses to define
        the actual job execution logic.

        Args:
            **kwargs: Job parameters.

        Returns:
            Job execution result.
        """
        pass

    @staticmethod
    def _get_findings_by_type(
        findings: list[Finding],
    ) -> dict[InputType, list[Finding]]:
        """Group findings by their input type.

        Args:
            findings: List of findings to group.

        Returns:
            Dictionary mapping input types to lists of findings.
        """
        findings_by_type = {}
        for finding in findings:
            if finding.input_type not in findings_by_type:
                findings_by_type[finding.input_type] = [finding]
            else:
                findings_by_type[finding.input_type].append(finding)
        # Sort findings by the number of related input types (to prioritize those with fewer dependencies)
        return dict(sorted(findings_by_type.items(), key=lambda i: len(i[0].related_input_types)))

    @staticmethod
    def calculate_executions(
        tool: Tool,
        findings: list[Finding],
        target_ports: list[TargetPort],
        input_vulnerabilities: list[InputVulnerability],
        input_technologies: list[InputTechnology],
        wordlists: list[Wordlist],
    ) -> list[ExecutionParametersToEnqueue]:
        """Calculate execution parameters for a tool.

        This method determines how to split the input data into separate
        executions based on tool configuration and input relationships.

        Args:
            tool: The tool to calculate executions for.
            findings: List of findings to process.
            target_ports: List of target ports to process.
            input_vulnerabilities: List of input vulnerabilities to process.
            input_technologies: List of input technologies to process.
            wordlists: List of wordlists to process.

        Returns:
            List of ExecutionParametersToEnqueue instances representing
            separate executions.
        """
        input_types_used = set()
        # Start with a single empty execution batch
        executions = [ExecutionParametersToEnqueue()]
        findings_by_type = BaseQueue._get_findings_by_type(findings)
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
            # For each tool input that matches the input type, ordered by priority order
            for tool_input in Input.objects.filter(argument__tool=tool, type=input_type).order_by("order"):
                # Filter base inputs according to the tool input's filter logic
                filtered_base_inputs = [bi for bi in source if bi.filter(tool_input)]
                if not filtered_base_inputs:
                    continue
                # Find related input types (dependencies) for this input type
                related_input_types = [i for i in input_type.related_input_types if i in findings_by_type]
                for execution_index, execution in enumerate(copy.deepcopy(executions)):
                    base_inputs = filtered_base_inputs.copy()
                    # If this is a finding and has related input types, only include those related to the current execution
                    if field == "findings" and related_input_types:
                        base_inputs = []
                        for related_input_type in related_input_types:
                            base_inputs.extend(
                                bi
                                for bi in filtered_base_inputs
                                if getattr(bi, related_input_type.name.lower()) in execution.findings
                                and bi not in base_inputs
                            )
                        if not base_inputs:
                            continue
                    input_types_used.add(input_type)
                    # If the tool argument allows multiple values, extend the execution batch
                    if tool_input.argument.multiple:
                        executions[execution_index].extend(field, base_inputs)
                    else:
                        # For single-value arguments, create a new execution batch for each additional value
                        original_execution = copy.deepcopy(execution)
                        executions[execution_index].append(field, base_inputs[0])
                        for base_input in base_inputs[1:]:
                            new_execution = copy.deepcopy(original_execution)
                            new_execution.append(field, base_input)
                            executions.append(new_execution)
                break  # One valid input type is enough
        return executions
