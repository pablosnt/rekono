"""Searchsploit executor for exploit database searches.

Executes Searchsploit tool to search the Exploit Database for available
exploits and proof-of-concepts based on technologies and vulnerabilities.
"""

from findings.models import Finding, Technology, Vulnerability
from parameters.models import InputTechnology, InputVulnerability
from target_ports.models import TargetPort
from tools.executors.base import BaseExecutor
from wordlists.models import Wordlist


class Searchsploit(BaseExecutor):
    """Executor for Searchsploit exploit database search tool.

    Handles Searchsploit execution for searching exploits and shellcodes
    in the Exploit Database. Validates that required technology or CVE
    parameters are available before execution.

    Attributes:
        Inherits all attributes from BaseExecutor
    """

    def get_arguments(
        self,
        findings: list[Finding],
        target_ports: list[TargetPort],
        input_vulnerabilities: list[InputVulnerability],
        input_technologies: list[InputTechnology],
        wordlists: list[Wordlist],
    ) -> list[str]:
        """Generate command-line arguments with validation for Searchsploit execution.

        Validates that either technology or CVE parameters are available for
        meaningful exploit searches before allowing execution.

        Args:
            findings (list[Finding]): Security findings to use as inputs
            target_ports (list[TargetPort]): Target ports to use as inputs
            input_vulnerabilities (list[InputVulnerability]): Vulnerability parameters
            input_technologies (list[InputTechnology]): Technology parameters
            wordlists (list[Wordlist]): Wordlists to use as inputs

        Returns:
            list[str]: Generated command-line arguments

        Raises:
            RuntimeError: If neither technology nor CVE arguments are available
        """
        arguments = super().get_arguments(findings, target_ports, input_vulnerabilities, input_technologies, wordlists)
        print(arguments)
        print(self.targets_used_in_execution)
        print(self.findings_used_in_execution)
        if (
            InputVulnerability not in self.targets_used_in_execution
            and InputTechnology not in self.targets_used_in_execution
            and Vulnerability not in self.findings_used_in_execution
            and Technology not in self.findings_used_in_execution
        ):
            raise RuntimeError(
                f"Argument 'technology' or 'cve' is required to execute tool '{self.execution.configuration.tool.name}'"
            )
        return arguments
