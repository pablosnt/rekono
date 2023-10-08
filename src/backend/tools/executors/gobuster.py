from typing import List

from findings.models import Finding
from input_types.models import BaseInput
from tools.executors.base import BaseExecutor


class Gobuster(BaseExecutor):
    def _get_arguments(
        self,
        findings: List[Finding],
        target_ports_and_parameters: List[BaseInput],
    ) -> List[str]:
        arguments = super()._get_arguments(findings, target_ports_and_parameters)
        if "--url" not in arguments and "--domain" not in arguments:
            raise RuntimeError(
                f"Argument 'url' or 'domain' is required to execute tool '{self.execution.configuration.tool.name}'"
            )
        if "--wordlist" not in arguments:
            raise RuntimeError(
                f"Argument 'wordlist' is required to execute tool '{self.execution.configuration.tool.name}'"
            )
        return arguments
