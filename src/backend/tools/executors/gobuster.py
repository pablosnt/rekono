"""Gobuster executor for directory and subdomain enumeration.

Executes Gobuster tool for brute force discovery of directories, files,
subdomains, and virtual hosts with validation of required parameters.
"""

from findings.models import Finding
from parameters.models import InputTechnology, InputVulnerability
from target_ports.models import TargetPort
from tools.executors.base import BaseExecutor
from wordlists.models import Wordlist


class Gobuster(BaseExecutor):
    """Executor for Gobuster directory and subdomain enumeration tool.

    Handles Gobuster execution for brute force enumeration operations.
    Validates that required URL/domain and wordlist parameters are available
    before allowing execution to proceed.
    
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
        """Generate command-line arguments with validation for Gobuster execution.
        
        Validates that required URL or domain parameters and wordlist are available
        for meaningful enumeration operations before allowing execution.
        
        Args:
            findings (list[Finding]): Security findings to use as inputs
            target_ports (list[TargetPort]): Target ports to use as inputs
            input_vulnerabilities (list[InputVulnerability]): Vulnerability parameters
            input_technologies (list[InputTechnology]): Technology parameters
            wordlists (list[Wordlist]): Wordlists to use as inputs
            
        Returns:
            list[str]: Generated command-line arguments
            
        Raises:
            RuntimeError: If required URL/domain or wordlist arguments are missing
        """
        arguments = super().get_arguments(findings, target_ports, input_vulnerabilities, input_technologies, wordlists)
        if "--url" not in arguments and "--domain" not in arguments:
            raise RuntimeError(
                f"Argument 'url' or 'domain' is required to execute tool '{self.execution.configuration.tool.name}'"
            )
        if "--wordlist" not in arguments:
            raise RuntimeError(
                f"Argument 'wordlist' is required to execute tool '{self.execution.configuration.tool.name}'"
            )
        return arguments
