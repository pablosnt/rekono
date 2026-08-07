"""Base classes for the background job queues based on RQ.

Besides the common job management, this module implements the calculation of the
executions to be enqueued for a tool configuration, which decides how the available
inputs are distributed among the executions of that tool.
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
    """Inputs that one tool execution will receive.

    Implements equality and hashing over its five lists so that identical
    executions can be deduplicated before being enqueued.

    Attributes:
        findings: Findings from previous executions used as input.
        target_ports: Target ports defined for the target.
        input_vulnerabilities: Vulnerabilities provided by the auditor.
        input_technologies: Technologies provided by the auditor.
        wordlists: Wordlists to be used by the tool.
    """

    findings: list[Finding]
    target_ports: list[TargetPort]
    input_vulnerabilities: list[InputVulnerability]
    input_technologies: list[InputTechnology]
    wordlists: list[Wordlist]

    def append(self, field: str, value: BaseInput) -> None:
        """Add one input to the list with the given field name.

        Args:
            field: Name of the attribute holding the list to extend.
            value: Input to add to it.
        """
        setattr(self, field, getattr(self, field) + [value])

    def extend(self, field: str, values: list[BaseInput]) -> None:
        """Add several inputs to the list with the given field name.

        Args:
            field: Name of the attribute holding the list to extend.
            values: Inputs to add to it.
        """
        setattr(self, field, getattr(self, field) + values)

    def __eq__(self, other: Any) -> bool:
        """Check if another object contains exactly the same inputs.

        Args:
            other: Object to compare with this one.

        Returns:
            Whether both objects hold the same inputs. False for any object of a
            different type.
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
        """Return a hash of all the inputs, so equal executions collapse in a set."""
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
    """Base queue where Rekono enqueues the jobs that it runs in the background.

    Attributes:
        name: Name of the RQ queue, which must be one of the queues configured in
          the RQ_QUEUES setting.
    """

    name = ""

    @cached_property
    def queue(self) -> Queue:
        """The RQ queue where the jobs of this class are enqueued."""
        return django_rq.get_queue(self.name)

    def fetch_job(self, job_id: str) -> Job | None:
        """Get a job from the queue.

        Args:
            job_id: Identifier returned by RQ when the job was enqueued.

        Returns:
            The job, or None if it doesn't exist anymore or it can't be
            deserialized because its code changed since it was enqueued.
        """
        try:
            return self.queue.fetch_job(job_id)
        except Exception:
            return None

    def cancel_job(self, job_id: str) -> None:
        """Cancel a job, doing nothing if it doesn't exist anymore.

        Args:
            job_id: Identifier returned by RQ when the job was enqueued.
        """
        job = self.fetch_job(job_id)
        if job:
            self.logger.info(f"[{self.name}] Job {job_id} has been cancelled")
            job.cancel()

    def delete_job(self, job_id: str) -> None:
        """Delete a job, doing nothing if it doesn't exist anymore.

        Args:
            job_id: Identifier returned by RQ when the job was enqueued.
        """
        job = self.fetch_job(job_id)
        if job:
            self.logger.info(f"[{self.name}] Job {job_id} has been deleted")
            job.delete()

    def enqueue(self, *args: Any, **kwargs: Any) -> Job:
        """Enqueue a new job that will be processed by the consume method.

        Args:
            *args: Arguments for the consume method.
            **kwargs: Arguments for the consume method, plus the RQ options like
              ``depends_on`` or ``on_success``.

        Returns:
            The enqueued job, whose identifier is what the queues keep to fetch,
            cancel, or delete it later.
        """
        return self.queue.enqueue(self.consume, *args, **kwargs)

    @staticmethod
    def consume(**kwargs: Any) -> Any:
        """Process one job of the queue, as implemented by each queue.

        Called by the RQ worker instead of by Rekono, so its arguments are the ones
        that enqueue received, unpickled in the worker process.

        Args:
            **kwargs: Arguments that enqueue received. Each queue replaces this
              signature with the named arguments that it needs.

        Returns:
            The value that RQ stores as the job result, which is what the success
            callbacks and the jobs depending on this one receive.
        """
        pass


class BaseScanQueue(BaseQueue):
    """Base queue of the ones that plan the executions of the scanning tools."""

    @staticmethod
    def _get_findings_by_type(
        findings: list[Finding],
    ) -> dict[InputType, list[Finding]]:
        """Group the findings by input type.

        Args:
            findings: Findings reported by the previous executions of a task.

        Returns:
            The findings grouped by input type, ordered so parent types (e.g. Host)
            come before their children (e.g. Port, Path).
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
        """Distribute the available inputs among the executions of a configuration.

        Only the input types that the configuration accepts are used, and only one
        input per type: the first tool input, by priority order, that isn't filtered
        out. How many executions are needed depends on the arguments of the tool,
        since an argument that only supports one value forces a new execution for
        each extra input.

        Args:
            configuration: Tool configuration whose inputs are being calculated.
            findings: Findings from previous executions of the same task.
            target_ports: Target ports defined for the target.
            input_vulnerabilities: Vulnerabilities provided by the auditor.
            input_technologies: Technologies provided by the auditor.
            wordlists: Wordlists selected for the task.

        Returns:
            The inputs of each execution to be enqueued, which is always at least
            one: a configuration that accepts none of the available inputs gets a
            single execution with no inputs at all.
        """
        input_types_used = set()
        executions = [ExecutionParametersToEnqueue([], [], [], [], [])]
        findings_by_type = BaseScanQueue._get_findings_by_type(findings)
        for field, source in [("findings", _findings) for _findings in findings_by_type.values()] + [
            ("target_ports", target_ports),
            ("input_vulnerabilities", input_vulnerabilities),
            ("input_technologies", input_technologies),
            ("wordlists", wordlists),
        ]:
            if not source:
                continue
            input_type = source[0].input_type
            if input_type in input_types_used:
                continue
            for tool_input in Input.objects.filter(argument__configuration=configuration, type=input_type).order_by(
                "order"
            ):
                filtered_base_inputs = [bi for bi in source if bi.filter(tool_input)]
                if not filtered_base_inputs:
                    continue
                # Only the parent input types that this configuration consumes as inputs, since the
                # parent findings of the other ones are never added to any execution, and grouping
                # the children by them would discard every child
                parent_input_types = [
                    i
                    for i in input_type.parent_input_types
                    if i in findings_by_type
                    and Input.objects.filter(argument__configuration=configuration, type=i).exists()
                ]
                for execution_index, execution in enumerate(copy.deepcopy(executions)):
                    if field == "findings" and parent_input_types:
                        # Keep each execution consistent: its ports and paths must belong to the
                        # host that the execution already includes, instead of to any other one
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
                    if tool_input.argument.multiple:
                        executions[execution_index].extend(field, base_inputs)
                    else:
                        # The argument only supports one value, so the first input stays in this
                        # execution and each extra one gets a copy of the execution for itself
                        original_execution = copy.deepcopy(execution)
                        executions[execution_index].append(field, base_inputs[0])
                        for base_input in base_inputs[1:]:
                            executions.append(copy.deepcopy(original_execution))
                            executions[-1].append(field, base_input)
                break  # One valid input type is enough
        return executions
