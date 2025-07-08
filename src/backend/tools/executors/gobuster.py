from findings.models import Finding
from parameters.models import InputTechnology, InputVulnerability
from target_ports.models import TargetPort
from tools.executors.base import BaseExecutor
from wordlists.models import Wordlist


class Gobuster(BaseExecutor):
    def _get_arguments(
        self,
        findings: list[Finding],
        target_ports: list[TargetPort],
        input_vulnerabilities: list[InputVulnerability],
        input_technologies: list[InputTechnology],
        wordlists: list[Wordlist],
    ) -> list[str]:
        arguments = super()._get_arguments(findings, target_ports, input_vulnerabilities, input_technologies, wordlists)
        if "--url" not in arguments and "--domain" not in arguments:
            raise RuntimeError(
                f"Argument 'url' or 'domain' is required to execute tool '{self.execution.configuration.tool.name}'"
            )
        if "--wordlist" not in arguments:
            raise RuntimeError(
                f"Argument 'wordlist' is required to execute tool '{self.execution.configuration.tool.name}'"
            )
        return arguments
