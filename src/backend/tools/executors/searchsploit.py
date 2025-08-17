from findings.models import Finding
from parameters.models import InputTechnology, InputVulnerability
from target_ports.models import TargetPort
from tools.executors.base import BaseExecutor
from wordlists.models import Wordlist


class Searchsploit(BaseExecutor):
    def get_arguments(
        self,
        findings: list[Finding],
        target_ports: list[TargetPort],
        input_vulnerabilities: list[InputVulnerability],
        input_technologies: list[InputTechnology],
        wordlists: list[Wordlist],
    ) -> list[str]:
        arguments = super().get_arguments(findings, target_ports, input_vulnerabilities, input_technologies, wordlists)
        if "--cve" not in arguments and len(arguments) == 3:
            raise RuntimeError(
                f"Argument 'technology' or 'cve' is required to execute tool '{self.execution.configuration.tool.name}'"
            )
        return arguments
