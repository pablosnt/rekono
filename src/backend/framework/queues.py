import logging
from typing import Any, Dict, List

import django_rq
from findings.framework.models import Finding
from framework.models import BaseInput
from input_types.models import InputType
from parameters.models import InputTechnology, InputVulnerability
from rq.job import Job
from target_ports.models import TargetPort
from tools.models import Input, Tool
from wordlists.models import Wordlist

logger = logging.getLogger()


class BaseQueue:
    def __init__(self, name: str) -> None:
        self.name = name
        self.queue = django_rq.get_queue(name)

    def cancel_job(self, job_id: str) -> Job:
        job = self.queue.fetch_job(job_id)
        if job:
            logger.info(f"[{self.name}] Job {job_id} has been cancelled")
            job.cancel()

    def delete_job(self, job_id: str) -> Job:
        job = self.queue.fetch_job(job_id)
        if job:
            logger.info(f"[{self.name}] Job {job_id} has been deleted")
            job.delete()

    def enqueue(self, **kwargs: Any) -> Job:
        return self.queue.enqueue(self.consume.__func__, **kwargs)

    def consume(self, **kwargs: Any) -> Any:
        pass

    def _calculate_executions(
        self,
        tool: Tool,
        findings: List[Finding],
        target_ports: List[TargetPort],
        input_vulnerabilities: List[InputVulnerability],
        input_technologies: List[InputTechnology],
        wordlists: List[Wordlist],
    ) -> List[Dict[int, List[BaseInput]]]:
        executions = [{0: []}]
        input_types_used = set()
        findings_by_type = {
            t: [f for f in findings if f.get_input_type() == t]
            for t in InputType.objects.all()
        }
        findings_by_type = dict(
            sorted(
                findings_by_type.items(),
                key=lambda i: len(i[0].get_related_input_types()),
            )
        )
        for index, input_type, source in (
            [(0, t, list(f)) for t, f in findings_by_type.values() if f]
            if findings_by_type
            else []
        ) + [
            (index + 1, None, p)
            for p in [
                target_ports,
                input_vulnerabilities,
                input_technologies,
                wordlists,
            ]
        ]:
            if not source:
                continue
            if not input_type:
                input_type = source[0].get_input_type()
                if input_type in input_types_used:
                    continue
            argument_inputs = Input.objects.filter(
                argument__tool=tool, type=input_type
            ).order_by("order")
            filtered_base_inputs = [
                base_input
                for base_input in source
                if len([i for i in argument_inputs if base_input.filter(i)]) > 0
            ]
            if not filtered_base_inputs:
                continue
            argument_input = argument_inputs.first().argument
            related_input_types = input_type.get_related_input_types()
            for execution in executions:
                if not execution.get(index):
                    execution[index] = []
                related_base_inputs = filtered_base_inputs.copy()
                if index == 0 and related_input_types:
                    related_base_inputs = []
                    for existing_base_input in execution[index]:
                        existing_input_type = base_input.get_input_type()
                        if existing_input_type in related_input_types:
                            related_base_inputs.extend(
                                [
                                    f
                                    for f in filtered_base_inputs
                                    if getattr(f, existing_input_type.name.lower())
                                    == existing_base_input
                                ]
                            )
                    if not related_base_inputs:
                        continue
                if argument_input.multiple:
                    execution[index].extend(related_base_inputs)
                    input_types_used.add(input_type)
                else:
                    original_execution = execution.copy()
                    input_types_used.add(input_type)
                    execution[index].append(related_base_inputs[0])
                    for base_input in related_base_inputs[1:]:
                        executions.append(original_execution)
                        executions[-1][index].append(base_input)
        return executions
