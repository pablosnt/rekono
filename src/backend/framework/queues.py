import copy
import logging
from typing import Any

import django_rq
from findings.framework.models import Finding
from framework.models import BaseInput
from input_types.models import InputType
from parameters.models import InputTechnology, InputVulnerability
from rq.job import Job
from rq.queue import Queue
from target_ports.models import TargetPort
from tools.models import Input, Tool
from wordlists.models import Wordlist

logger = logging.getLogger()


class BaseQueue:
    name = ""

    def _get_queue(self) -> Queue:
        return django_rq.get_queue(self.name)

    def _fetch_job(self, job_id: str) -> Job | None:
        try:
            return self._get_queue().fetch_job(job_id)
        except Exception:
            return None

    def cancel_job(self, job_id: str) -> None:
        job = self._fetch_job(job_id)
        if job:
            logger.info(f"[{self.name}] Job {job_id} has been cancelled")
            job.cancel()

    def delete_job(self, job_id: str) -> None:
        job = self._fetch_job(job_id)
        if job:
            logger.info(f"[{self.name}] Job {job_id} has been deleted")
            job.delete()

    def enqueue(self, **kwargs: Any) -> Job:
        return self._get_queue().enqueue(self.consume, **kwargs)

    @staticmethod
    def consume(**kwargs: Any) -> Any:
        pass

    @staticmethod
    def _get_findings_by_type(
        findings: list[Finding],
    ) -> dict[InputType, list[Finding]]:
        findings_by_type = {}
        for finding in findings:
            input_type = finding.get_input_type()
            if input_type not in findings_by_type:
                findings_by_type[input_type] = [finding]
            else:
                findings_by_type[input_type].append(finding)
        return dict(
            sorted(
                findings_by_type.items(),
                key=lambda i: len(i[0].get_related_input_types()),
            )
        )

    @staticmethod
    def _calculate_executions(
        tool: Tool,
        findings: list[Finding],
        target_ports: list[TargetPort],
        input_vulnerabilities: list[InputVulnerability],
        input_technologies: list[InputTechnology],
        wordlists: list[Wordlist],
    ) -> list[dict[int, list[BaseInput]]]:
        executions: list[dict[int, list[BaseInput]]] = [{i: []} for i in range(5)]
        input_types_used = set()
        findings_by_type = BaseQueue._get_findings_by_type(findings)
        for index, input_type, source in [
            (0, t, list(f)) for t, f in (findings_by_type or {}).items() if f
        ] + [
            (i + 1, None, p)
            for i, p in enumerate(
                [
                    target_ports,
                    input_vulnerabilities,
                    input_technologies,
                    wordlists,
                ]
            )
        ]:
            if not source:
                continue
            if not input_type:
                input_type = source[0].get_input_type()
                if input_type in input_types_used:
                    continue
            tool_input = (
                Input.objects.filter(argument__tool=tool, type=input_type)
                .order_by("order")
                .first()
            )
            if not tool_input:
                continue
            filtered_base_inputs = [bi for bi in source if bi.filter(tool_input)]
            if not filtered_base_inputs:
                continue
            related_input_types = [
                i for i in input_type.get_related_input_types() if i in findings_by_type
            ]
            for execution_index, execution in enumerate(copy.deepcopy(executions)):
                if not executions[execution_index].get(index):
                    executions[execution_index][index] = []
                base_inputs = filtered_base_inputs.copy()
                if index == 0 and related_input_types:
                    base_inputs = []
                    for related_input_type in related_input_types:
                        base_inputs.extend(
                            bi
                            for bi in filtered_base_inputs
                            if getattr(bi, related_input_type.name.lower())
                            in execution[index]
                            and bi not in base_inputs
                        )
                    if not base_inputs:
                        continue
                input_types_used.add(input_type)
                if tool_input.argument.multiple:
                    executions[execution_index][index].extend(base_inputs)
                else:
                    original_execution = copy.deepcopy(execution)
                    executions[execution_index][index].append(base_inputs[0])
                    for base_input in base_inputs[1:]:
                        executions.append(copy.deepcopy(original_execution))
                        if not executions[-1].get(index):
                            executions[-1][index] = [base_input]
                        else:
                            executions[-1][index].append(base_input)
        return executions
