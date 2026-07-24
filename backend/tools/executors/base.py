"""Base executor class for security tool execution and management.

Provides the foundation for executing security tools with proper parameter
generation, environment setup, and execution lifecycle management. All
tool-specific executors inherit from BaseExecutor.
"""

import os
import re
import subprocess
import sys
import uuid
from functools import cached_property
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from django.core.exceptions import ValidationError
from django.forms.models import model_to_dict

from authentications.models import Authentication
from executions.models import Execution
from findings.framework.models import Finding
from findings.models import Port
from framework.enums import InputKeyword
from framework.logging import LoggingEntity
from http_headers.models import HttpHeader
from parameters.models import InputTechnology, InputVulnerability
from rekono.settings import BASE_DIR, CONFIG
from security.cryptography import Crypto
from security.validators.enums import Regex
from security.validators.input_validator import Validator
from settings.models import Settings
from target_ports.models import TargetPort
from tools.models import Intensity
from wordlists.models import Wordlist


class BaseExecutor(LoggingEntity):
    """Base executor class for security tool execution with comprehensive parameter management.

    Handles the complete execution lifecycle of security tools including argument generation,
    environment setup, execution control, and status tracking. Provides automatic parameter
    mapping from available inputs and configurations with proper authentication handling.

    Attributes:
        environment_validator (Validator): Rejects sensitive environment variable assignments

    Example:
        Execute a tool with proper parameter generation:

        ```python
        executor = SomeToolExecutor(execution)
        executor.execute(findings, target_ports, vulns, techs, wordlists)
        ```
    """

    environment_validator = Validator(Regex.SENSITIVE_ENV, inverse_match=False)

    def __init__(self, execution: Execution) -> None:
        """Initialize the executor with execution context and configuration.

        Sets up the executor with the execution instance, determines appropriate
        intensity level, generates report file path, and configures execution directory.

        Args:
            execution (Execution): The execution instance to manage
        """
        self.arguments = []
        self.environment = {}
        self.hashable_environment = {}
        self.findings_used_in_execution = {}
        self.targets_used_in_execution = {}
        self.authentication = None
        # This will save the port included in URL or TARGET parameters
        # so, we have the scanned port independently of its source, i.e.
        # port found in previous execution, target port or default URL port
        self.port_from_arguments = None
        self.execution = execution
        self.intensity = (
            Intensity.objects.filter(tool=execution.configuration.tool, value__lte=execution.task.intensity)
            .order_by("-value")
            .first()
        )
        self.report = CONFIG.reports / f"{str(uuid.uuid4())}.{execution.configuration.tool.output_format or 'txt'}"
        self.execution_directory = (
            getattr(CONFIG, self.execution.configuration.tool.run_directory_property.lower())
            if self.execution.configuration.tool.run_directory_property
            else None
        )

    @cached_property
    def scanned_port(self) -> int | None:
        """Get the port that is being scanned by this execution.

        Determines the port being scanned by prioritizing ports extracted from
        execution arguments over the tool's default scanned port configuration.

        Returns:
            int | None: The port number being scanned, or None if not applicable
        """
        return (
            self.port_from_arguments
            if self.port_from_arguments is not None
            else self.execution.configuration.default_scanned_port
        )

    @property
    def hash(self) -> str:
        """Build a stable fingerprint of the execution for finding deduplication.

        Combines the run environment and the command arguments into a single
        lowercased string and hashes it. Arguments that reference the report path
        are dropped because that path changes on every run, so identical scans of
        the same target produce the same hash.

        Returns:
            str: Hash identifying equivalent executions.
        """
        return Crypto.hash(
            " ".join(
                [f"{k}={v}" for k, v in self.hashable_environment.items()]
                + [a for a in self.arguments if str(self.report).lower() not in a.lower()]
            ).lower()
        )

    def get_arguments(
        self,
        findings: list[Finding],
        target_ports: list[TargetPort],
        input_vulnerabilities: list[InputVulnerability],
        input_technologies: list[InputTechnology],
        wordlists: list[Wordlist],
    ) -> list[str]:
        """Generate command-line arguments for tool execution.

        Automatically maps available inputs to tool arguments based on tool configuration.
        Processes findings, target ports, vulnerabilities, technologies, and wordlists
        to generate properly formatted command-line arguments.

        Args:
            findings (list[Finding]): Security findings to use as inputs
            target_ports (list[TargetPort]): Target ports to use as inputs
            input_vulnerabilities (list[InputVulnerability]): Vulnerability parameters
            input_technologies (list[InputTechnology]): Technology parameters
            wordlists (list[Wordlist]): Wordlists to use as inputs

        Returns:
            list[str]: Generated command-line arguments

        Raises:
            RuntimeError: If required arguments cannot be satisfied with available inputs
        """
        # Initialize base parameters available to all tools (script path, command, intensity, output)
        parameters = {
            "script": (
                (
                    Path(
                        getattr(
                            CONFIG,
                            self.execution.configuration.tool.script_directory_property.lower(),
                        )
                    )
                    / self.execution.configuration.tool.script
                )
                if self.execution.configuration.tool.script_directory_property
                and self.execution.configuration.tool.script
                else ""
            ),
            "command": self.execution.configuration.tool.command,
            "intensity": self.intensity.argument,
            "output": self.report if self.execution.configuration.tool.output_format else "",
        }
        # For each configuration argument, find the best input source that satisfies the argument requirements
        for argument in self.execution.configuration.arguments.all():
            for argument_input in argument.inputs.all().order_by("order"):
                parsed_data: dict[str, Any] = {}
                # Track if we already have data from the primary base inputs
                has_primary_model_data = False
                # Create a comprehensive list of all available input sources in priority order
                # This includes findings, wordlists, authentications, targets, HTTP headers and user-provided parameters
                for base_input in (
                    findings
                    + list(wordlists)
                    + list(
                        Authentication.objects.filter(
                            # TDOO: Why all the autheticatios fro the target can be used!
                            target_port__target=self.execution.task.target,
                            target_port__port__in=[
                                f.port if isinstance(f, Port) else f.port.port
                                for f in findings
                                if isinstance(f, Port) or (hasattr(f, "port") and isinstance(f.port, Port))
                            ],
                        ).all()
                    )
                    + [self.execution.task.target]
                    + list(target_ports)
                    + [p.authentication for p in target_ports if hasattr(p, "authentication")]
                    + list(input_vulnerabilities)
                    + list(input_technologies)
                    + list(HttpHeader.objects.filter(target__isnull=True, user__isnull=True).all())
                    + (list(self.execution.task.executor.http_headers.all()) if self.execution.task.executor else [])
                    + list(self.execution.task.target.http_headers.all())
                ):
                    # Check if this input matches the argument's fallback type (less preferred)
                    is_fallback = argument_input.type.fallback_model_class and isinstance(
                        base_input, argument_input.type.fallback_model_class
                    )
                    # If we already have data from primary sources, skip fallback inputs
                    if is_fallback and has_primary_model_data:
                        break
                    # Check if this input matches the argument's primary type (preferred)
                    is_model = argument_input.type.model_class and isinstance(
                        base_input, argument_input.type.model_class
                    )
                    # Skip inputs that don't match either primary or fallback types
                    if not is_model and not is_fallback:
                        continue
                    # Apply input-specific filtering to ensure compatibility with tool requirements
                    if base_input.filter(argument_input, self.execution.task.target):
                        # Parse the input data and accumulate results
                        parsed_data = base_input.parse(self.execution.task, parsed_data)
                        # Track which inputs are being used for this execution
                        if is_fallback:
                            self.targets_used_in_execution[base_input.__class__] = base_input
                        else:
                            self.findings_used_in_execution[base_input.__class__] = base_input
                            has_primary_model_data = True
                        # Store authentication credentials for later use
                        if isinstance(base_input, Authentication):
                            self.authentication = base_input
                        # For single-value arguments, stop after finding the first valid input
                        if not argument.multiple:
                            break
                # Stop searching for more argument inputs once we have valid data
                if parsed_data:
                    break
            if parsed_data:
                if self.port_from_arguments is None:
                    url_key = InputKeyword.URL.name.lower()
                    port_key = InputKeyword.PORT.name.lower()
                    try:
                        if f"{{{port_key}}}" in argument.argument and parsed_data.get(port_key):
                            self.port_from_arguments = int(parsed_data[port_key])
                        if f"{{{url_key}}}" in argument.argument and parsed_data.get(url_key):
                            self.port_from_arguments = urlparse(parsed_data[url_key]).port
                    except Exception:
                        pass
                try:
                    # Special handling for HTTP headers - format each header individually then join
                    if InputKeyword.HEADERS.name.lower() in parsed_data:
                        parameters[argument.name] = " ".join(
                            [
                                argument.argument.format(
                                    **{
                                        InputKeyword.HEADER_KEY.name.lower(): k,
                                        InputKeyword.HEADER_VALUE.name.lower(): v,
                                    }
                                )
                                for k, v in parsed_data.get(InputKeyword.HEADERS.name.lower(), {}).items()
                            ]
                        )
                    else:
                        # Standard parameter formatting using argument template with parsed data
                        parameters[argument.name] = argument.argument.format(**parsed_data)
                except KeyError:
                    # A placeholder couldn't be resolved (e.g. no reachable URL), so skip the
                    # execution when the argument is required, otherwise drop the argument
                    if argument.required:
                        raise RuntimeError(
                            f"Argument '{argument.name}' is required to execute configuration "
                            f"'{argument.configuration.name}'"
                        )
                    parameters[argument.name] = ""
            elif not argument.required:
                parameters[argument.name] = ""
            else:
                raise RuntimeError(
                    f"Argument '{argument.name}' is required to execute configuration '{argument.configuration.name}'"
                )
        # Parse formatted command arguments into list, handling quoted strings properly
        # Remove quotes from individual arguments to prevent shell escaping issues
        return [
            a.replace('"', "")
            for a in re.findall(
                r'[^\s\'"]*[\'"][^\'"]+[\'"]|[^\'"\s]+',
                self.execution.configuration.command_template.format(**parameters),
            )
        ]

    def check_arguments(
        self,
        findings: list[Finding],
        target_ports: list[TargetPort],
        input_vulnerabilities: list[InputVulnerability],
        input_technologies: list[InputTechnology],
        wordlists: list[Wordlist],
    ) -> bool:
        """Check if arguments can be generated with available inputs.

        Validates whether the tool can be executed with the provided inputs
        by attempting to generate arguments without raising exceptions.

        Args:
            findings (list[Finding]): Security findings to use as inputs
            target_ports (list[TargetPort]): Target ports to use as inputs
            input_vulnerabilities (list[InputVulnerability]): Vulnerability parameters
            input_technologies (list[InputTechnology]): Technology parameters
            wordlists (list[Wordlist]): Wordlists to use as inputs

        Returns:
            bool: True if arguments can be generated, False otherwise
        """
        try:
            self.get_arguments(findings, target_ports, input_vulnerabilities, input_technologies, wordlists)
            return True
        except RuntimeError:
            return False

    @classmethod
    def get_clean_default_environment(cls) -> dict[str, Any]:
        """Prepare base environment variables to run tools out of Rekono's virtualenv.

        Copies the system environment variables, removing Rekono's own virtualenv bin
        directory from PATH, so external tools that shell out to a bare `python3`
        (e.g. Dirsearch, EmailHarvester, Log4j Scan, Spring4Shell Scan) resolve the
        system interpreter, which has their required dependencies installed, instead
        of Rekono's isolated venv, which only has Rekono's own dependencies.

        Returns:
            dict[str, Any]: Environment variables without Rekono's virtualenv in PATH
        """
        environment = os.environ.copy()
        venv_bin = str(Path(sys.executable).parent)
        if environment.get("PATH") and venv_bin.startswith(str(BASE_DIR)):
            environment["PATH"] = os.pathsep.join(
                path for path in environment["PATH"].split(os.pathsep) if path != venv_bin
            )
        return environment

    def get_environment(self) -> dict[str, Any]:
        """Prepare environment variables for tool execution.

        Sets up the execution environment from the clean environment, processing
        tool-specific environment definitions, and configuring proxy settings from
        global configuration. Environment definitions parsed from the pre-command
        arguments are filtered so user-controlled values cannot set sensitive
        variables (PATH, LD_PRELOAD, etc.) that could hijack the subprocess.

        Returns:
            dict[str, Any]: Environment variables for tool execution
        """
        environment = self.get_clean_default_environment()
        # Ensure tool command is at the beginning of arguments list
        if self.execution.configuration.tool.command not in self.arguments:
            self.arguments.insert(0, self.execution.configuration.tool.command)
        else:
            # Tool command found in arguments - extract environment variables from prefix
            index = self.arguments.index(self.execution.configuration.tool.command)
            # Parse environment variable definitions that precede the tool command
            for definition in self.arguments[:index]:
                if "=" in definition:
                    variable, value = definition.split("=", 1)
                    try:
                        # Avoid malicious environment variables
                        self.environment_validator(definition)
                    except ValidationError:
                        self.logger.warning(
                            f"[Security] Refused to set sensitive environment variable '{variable}' from execution arguments"
                        )
                        continue
                    variable = variable.strip()
                    value = value.strip().replace("'", "").replace('"', "")
                    # Clean variable value by removing quotes that might interfere with execution
                    environment[variable] = value
                    self.hashable_environment[variable] = value
            # Remove environment definitions from arguments, keeping only the tool command and its parameters
            self.arguments = self.arguments[index:]
        settings = Settings.objects.first()
        for proxy in model_to_dict(Settings).keys():
            if "_proxy" in proxy and getattr(settings, proxy) is not None:
                # Add environment variables for proxy configuration
                environment[proxy.upper()] = getattr(settings, proxy)
        return environment

    def before_running(self) -> None:  # pragma: no cover
        """Hook method called before tool execution.

        Override this method in tool-specific executor classes to implement
        custom pre-execution logic such as additional setup or validation.
        """
        pass

    def run_tool(self, environment: dict[str, Any] = os.environ.copy()) -> None:  # pragma: no cover
        """Execute the security tool with configured arguments and environment.

        Runs the tool subprocess with proper output handling, status tracking,
        and error management. Handles both file-based and stdout-based output capture.

        Args:
            environment (dict[str, Any]): Environment variables for execution
        """
        self.logger.info(f"[Tool] Running: {self.mask_sensitive_data(' '.join(self.arguments))}")
        # Determine output capture strategy based on tool configuration
        # Use file-based output if tool has a specific format and report path isn't already in arguments
        stdout = (
            self.report
            if self.execution.configuration.tool.output_format
            and not any([str(self.report) in arg for arg in self.arguments])
            else None
        )
        if stdout:
            # File-based output: redirect tool output directly to report file
            with self.report.open("w") as _stdout:
                # Stderr is discarded as the stdout file will be used as stdout
                # and report, so stderr content would break the report format
                process = subprocess.run(self.arguments, stdout=_stdout, env=environment, cwd=self.execution_directory)
            # Read back the output for processing (ANSI cleanup, etc.)
            output = ""
            if self.report.is_file():
                with self.report.open("r") as _output:
                    output = _output.read()
        else:
            # Memory-based output: capture stdout/stderr in memory for immediate processing
            # Merge stderr into stdout to capture all tool messages in one stream
            process = subprocess.run(
                self.arguments,
                env=environment,
                cwd=self.execution_directory,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
            output = process.stdout
        # Store file reference if tool produces structured output format
        if self.execution.configuration.tool.output_format and self.report.is_file():
            self.execution.output_file = self.report
        # Clean tool output by removing ANSI escape sequences (colors, formatting)
        # This ensures consistent text processing for parsers and display
        self.execution.output_plain = re.sub(r"(\x9B|\x1B\[)[\d]*[ -\/]*[@-~]", "", output, flags=re.IGNORECASE)
        self.execution.save(update_fields=["output_plain", "output_file"])
        # Handle execution completion based on tool exit code and configuration
        # Some tools use non-zero exit codes for normal operation (e.g., findings detected)
        if not self.execution.configuration.tool.ignore_exit_code and process.returncode > 0:
            self.execution.error()
        else:
            self.execution.completed(self.hash)

    def after_running(self) -> None:  # pragma: no cover
        """Hook method called after tool execution.

        Override this method in tool-specific executor classes to implement
        custom post-execution logic such as output processing or cleanup.
        """
        pass

    def save_executed_command(self, wordlists: list[Wordlist]) -> None:
        """Build an anonymized string of the command that was executed.

        Reconstructs the command line from the finalized arguments and removes
        sensitive information (the internal report path, wordlist and script paths,
        and authentication secrets) so it can be safely persisted and shown to users.

        Args:
            wordlists (list[Wordlist]): Wordlists used to generate the command
        """
        command = " ".join(self.arguments)
        # Hide the internal reports directory
        if self.report:
            command = command.replace(
                str(self.report), f"output.{self.execution.configuration.tool.output_format or 'txt'}"
            )
        # Hide wordlist absolute paths
        for wordlist in wordlists:
            command = command.replace(wordlist.path, Path(wordlist.path).name)
        # Hide scripts absolute path
        if self.execution.configuration.tool.script and self.execution.configuration.tool.script_directory_property:
            command = command.replace(
                str(
                    Path(getattr(CONFIG, self.execution.configuration.tool.script_directory_property.lower()))
                    / self.execution.configuration.tool.script
                ),
                self.execution.configuration.tool.script,
            )
        # Hide every target's authentication secret
        self.execution.executed_command = self.mask_sensitive_data(command)
        self.execution.save(update_fields=["executed_command"])

    def mask_sensitive_data(self, command: str) -> str:
        """Mask every authentication secret reachable from the target in a command line.

        Replaces both the stored secret and its derived token, for all authentications
        configured on the target's ports, with a same-length mask of asterisks. Secrets
        are masked even when embedded inside other values, such as header values or Basic
        auth tokens.

        Args:
            command (str): The command line that may contain sensitive credentials

        Returns:
            str: The command line with every authentication secret and token masked
        """
        for authentication in Authentication.objects.filter(target_port__target=self.execution.task.target).all():
            for value in (authentication.secret, authentication.token):
                if value:
                    command = command.replace(value, "*" * len(value))
        return command

    def execute(
        self,
        findings: list[Finding],
        target_ports: list[TargetPort],
        input_vulnerabilities: list[InputVulnerability],
        input_technologies: list[InputTechnology],
        wordlists: list[Wordlist],
    ) -> None:
        """Execute the complete tool execution lifecycle.

        Manages the full execution process including status updates, argument generation,
        environment setup, tool execution, and cleanup. Handles errors and skipping
        conditions appropriately.

        Args:
            findings (list[Finding]): Security findings to use as inputs
            target_ports (list[TargetPort]): Target ports to use as inputs
            input_vulnerabilities (list[InputVulnerability]): Vulnerability parameters
            input_technologies (list[InputTechnology]): Technology parameters
            wordlists (list[Wordlist]): Wordlists to use as inputs
        """
        self.execution.started()
        self.execution.configuration.tool.update_status()
        if not self.execution.configuration.tool.is_installed:
            self.execution.skipped(f"Tool {self.execution.configuration.tool.name} is not installed in the system")
            return
        try:
            self.arguments = self.get_arguments(
                findings, target_ports, input_vulnerabilities, input_technologies, wordlists
            )
        except RuntimeError as error:
            self.logger.error(f"[Tool] {str(error)}")
            self.execution.skipped(str(error))
            return
        self.environment = self.get_environment()
        self.save_executed_command(wordlists)
        self.before_running()
        try:
            if not CONFIG.testing:
                self.run_tool(self.environment)
        except (RuntimeError, Exception):
            self.execution.error()
            self.after_running()
            return
        self.after_running()
