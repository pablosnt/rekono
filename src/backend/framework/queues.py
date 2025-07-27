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
    findings: list[Finding] = []
    target_ports: list[TargetPort] = []
    input_vulnerabilities: list[InputVulnerability] = []
    input_technologies: list[InputTechnology] = []
    wordlists: list[Wordlist] = []

    def append(self, field: str, value: BaseInput) -> None:
        setattr(self, field, getattr(self, field) + [value])

    def extend(self, field: str, values: list[BaseInput]) -> None:
        setattr(self, field, getattr(self, field) + values)

    def __eq__(self, other: Any) -> bool:
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
    name = ""

    @cached_property
    def queue(self) -> Queue:
        return django_rq.get_queue(self.name)

    def fetch_job(self, job_id: str) -> Job | None:
        try:
            return self.queue.fetch_job(job_id)
        except Exception:
            return None

    def cancel_job(self, job_id: str) -> None:
        job = self.fetch_job(job_id)
        if job:
            self.logger.info(f"[{self.name}] Job {job_id} has been cancelled")
            job.cancel()

    def delete_job(self, job_id: str) -> None:
        job = self.fetch_job(job_id)
        if job:
            self.logger.info(f"[{self.name}] Job {job_id} has been deleted")
            job.delete()

    def enqueue(self, *args: Any, **kwargs: Any) -> Job:
        return self.queue.enqueue(self.consume, *args, **kwargs)

    @staticmethod
    def consume(**kwargs: Any) -> Any:
        pass

    @staticmethod
    def _get_findings_by_type(
        findings: list[Finding],
    ) -> dict[InputType, list[Finding]]:
        findings_by_type = {}
        for finding in findings:
            if finding.input_type not in findings_by_type:
                findings_by_type[finding.input_type] = [finding]
            else:
                findings_by_type[finding.input_type].append(finding)
        return dict(
            sorted(
                findings_by_type.items(),
                key=lambda i: len(i[0].get_related_input_types()),
            )
        )

    @staticmethod
    def calculate_executions(
        tool: Tool,
        findings: list[Finding],
        target_ports: list[TargetPort],
        input_vulnerabilities: list[InputVulnerability],
        input_technologies: list[InputTechnology],
        wordlists: list[Wordlist],
    ) -> list[ExecutionParametersToEnqueue]:
        input_types_used = set()
        executions: list[dict[int, list[BaseInput]]] = [ExecutionParametersToEnqueue()]
        findings_by_type = BaseQueue._get_findings_by_type(findings)
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
            for tool_input in Input.objects.filter(argument__tool=tool, type=input_type).order_by("order"):
                filtered_base_inputs = [bi for bi in source if bi.filter(tool_input)]
                if not filtered_base_inputs:
                    continue
                related_input_types = [i for i in input_type.get_related_input_types() if i in findings_by_type]
                for execution_index, execution in enumerate(copy.deepcopy(executions)):
                    base_inputs = filtered_base_inputs.copy()
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
                    if tool_input.argument.multiple:
                        executions[execution_index].extend(base_inputs)
                    else:
                        original_execution = copy.deepcopy(execution)
                        executions[execution_index].append(field, base_inputs[0])
                        for base_input in base_inputs[1:]:
                            new_execution = copy.deepcopy(original_execution)
                            new_execution.append(field, base_input)
                            executions.append(new_execution)
                break  # One valid input type is enough
        return executions
