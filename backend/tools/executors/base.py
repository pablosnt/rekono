"""Base executor that builds and runs the command of a tool.

The tool-specific executors only override the hooks that they need, since the whole
lifecycle, from building the arguments to saving the output, is the same for all of
them.
"""

import os
import re
import shutil
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
from rekono.settings import CONFIG
from security.cryptography import Crypto
from security.validators.enums import Regex
from security.validators.input_validator import Validator
from settings.models import Settings
from target_ports.models import TargetPort
from tools.models import Intensity, Tool
from wordlists.models import Wordlist


class BaseExecutor(LoggingEntity):
    """Execution of one tool, from the arguments it needs to the output it writes.

    The commands are run as an argument list instead of through a shell, so nothing
    that reaches an argument can be interpreted as a shell metacharacter.

    Attributes:
        environment_validator: Rejects the environment variables that could hijack
          the tool process, like PATH or LD_PRELOAD.
        execution: Execution that is being run.
        arguments: Command of the execution, as the list that is run.
        environment: Environment variables that the tool is run with.
        hashable_environment: The ones of those variables that the command defined,
          which take part in the hash that identifies equivalent executions.
        findings_used_in_execution: Finding used as input for each finding type,
          which the parser links the new findings to.
        targets_used_in_execution: Target data used as input for each type, which
          the parser turns into findings when nothing was discovered yet.
        authentication: Authentication used against the target, whose secrets are
          masked in everything that the users can read.
        port_from_arguments: Port that the command scans, taken from its arguments.
        intensity: Intensity that the tool is run with, which is the closest one
          below the requested intensity among the ones that the tool supports.
        report: File where the tool writes its results.
        execution_directory: Directory where the tool is run, which is the one the
          tool was installed in when it declares one and a temporary one otherwise.
        temporary_execution_directory: Execution directory when Rekono created it for
          this execution, so it can be removed once the tool is done.
    """

    environment_validator = Validator(Regex.SENSITIVE_ENV, inverse_match=False)

    def __init__(self, execution: Execution) -> None:
        """Prepare the executor of an execution.

        Args:
            execution: Execution to be run.
        """
        self.arguments = []
        self.environment = {}
        self.hashable_environment = {}
        self.findings_used_in_execution = {}
        self.targets_used_in_execution = {}
        self.authentication = None
        self.port_from_arguments = None
        self.execution = execution
        # The tools don't support all the intensities, so the closest one below the requested
        # intensity is used instead of skipping the execution
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
        self.temporary_execution_directory = None

    @cached_property
    def scanned_port(self) -> int | None:
        """The port that this execution scans, or None if it doesn't scan one."""
        return (
            self.port_from_arguments
            if self.port_from_arguments is not None
            else self.execution.configuration.default_scanned_port
        )

    @property
    def hash(self) -> str:
        """Fingerprint of what this execution scans and how.

        Two executions with the same hash scanned the same thing in the same way, so
        the findings that one of them didn't discover anymore are considered fixed.
        """
        # The report path changes on every run, so the arguments that reference it are left
        # out to keep the hash stable
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
        """Build the command of the execution from the available data.

        Args:
            findings: Findings that the previous executions discovered.
            target_ports: Ports that the target defines.
            input_vulnerabilities: Vulnerabilities that the users provided.
            input_technologies: Technologies that the users provided.
            wordlists: Wordlists that the task uses.

        Returns:
            The command as a list of arguments, ready to be run without a shell.

        Raises:
            RuntimeError: If no available data can fill a required argument, which
              means that this execution can't be run.
        """
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
        for argument in self.execution.configuration.arguments.all():
            # The inputs of an argument are ordered by preference, so the first one with data
            # available is the one that fills it
            for argument_input in argument.inputs.all().order_by("order"):
                parsed_data: dict[str, Any] = {}
                has_primary_model_data = False
                for base_input in (
                    findings
                    + list(wordlists)
                    + list(
                        Authentication.objects.filter(
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
                    # The fallback data, like the target itself, is only used when no finding
                    # of the expected type has been discovered yet
                    is_fallback = argument_input.type.fallback_model_class and isinstance(
                        base_input, argument_input.type.fallback_model_class
                    )
                    if is_fallback and has_primary_model_data:
                        break
                    is_model = argument_input.type.model_class and isinstance(
                        base_input, argument_input.type.model_class
                    )
                    if not is_model and not is_fallback:
                        continue
                    if base_input.filter(argument_input, self.execution.task.target):
                        parsed_data = base_input.parse(self.execution.task, parsed_data)
                        if is_fallback:
                            self.targets_used_in_execution[base_input.__class__] = base_input
                        else:
                            self.findings_used_in_execution[base_input.__class__] = base_input
                            has_primary_model_data = True
                        if isinstance(base_input, Authentication):
                            self.authentication = base_input
                        if not argument.multiple:
                            break
                if parsed_data:
                    break
            if parsed_data:
                # The scanned port is taken from the first argument that includes one, so it's
                # known no matter where the port came from
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
                    # The headers are the only input that provides several values for one
                    # argument, so the argument is repeated once per header
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
        # Split the formatted command into individual arguments, keeping quoted segments
        # (e.g. a quoted header value or a secret containing spaces) together as a single
        # token. The two quote characters mean different things in an argument template,
        # because these arguments are passed directly to subprocess.run rather than through
        # a shell that would remove them:
        # - Single quotes only group, so they are stripped and the tool receives the bare
        #   value. This is what almost every argument needs
        # - Double quotes group as well, but are kept, so the tool receives them as part of
        #   the value. Only needed by tools that parse quotes themselves, like Nikto, whose
        #   STATIC-COOKIE option ignores any cookie that isn't written as "name=value"
        # A quoted value that ends up empty is still matched as a single token, so its quotes
        # can't be joined to the next argument and break the structure of the command
        return [
            a.replace("'", "")
            for a in re.findall(
                r'[^\s\'"]*[\'"][^\'"]*[\'"]|[^\'"\s]+',
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
        """Check if the execution can be run with the available data.

        Args:
            findings: Findings that the previous executions discovered.
            target_ports: Ports that the target defines.
            input_vulnerabilities: Vulnerabilities that the users provided.
            input_technologies: Technologies that the users provided.
            wordlists: Wordlists that the task uses.

        Returns:
            Whether the command could be built, which means that every required
            argument can be filled.
        """
        try:
            self.get_arguments(findings, target_ports, input_vulnerabilities, input_technologies, wordlists)
            return True
        except RuntimeError:
            return False

    @classmethod
    def is_installed(cls, tool: Tool) -> bool:
        """Check if everything that this executor needs is installed.

        Args:
            tool: Tool whose command and script are checked.

        Returns:
            Whether the command and the script of the tool are available, skipping
            the checks for the ones that the tool doesn't declare. The executors
            that need something else check it on top of this one.
        """
        if tool.command and not shutil.which(tool.command):
            return False
        if tool.script_directory_property:
            directory = Path(getattr(CONFIG, tool.script_directory_property.lower()))
            if not directory.is_dir() or not (directory / tool.script).is_file():
                return False
        return True

    @classmethod
    def get_clean_default_environment(cls) -> dict[str, Any]:
        """Get the environment variables to run a tool out of the Rekono virtualenv.

        Returns:
            The system environment without the Rekono virtualenv in the PATH, so
            the tools that call a bare python3 find the system interpreter, which
            is where their own dependencies are installed.
        """
        environment = os.environ.copy()
        if environment.get("PATH") and sys.prefix != sys.base_prefix:
            venv_bin = str(Path(sys.executable).parent)
            environment["PATH"] = os.pathsep.join(
                path for path in environment["PATH"].split(os.pathsep) if path != venv_bin
            )
        return environment

    def get_environment(self) -> dict[str, Any]:
        """Get the environment variables that the tool will be run with.

        Returns:
            The environment of the system, plus the proxies of the settings and the
            variables that the command defines before the tool command, without the
            ones that could hijack the tool process.
        """
        environment = self.get_clean_default_environment()
        if self.execution.configuration.tool.command not in self.arguments:
            self.arguments.insert(0, self.execution.configuration.tool.command)
        else:
            # Everything written before the tool command is an environment variable definition,
            # which is how a command template passes configuration to the tool
            index = self.arguments.index(self.execution.configuration.tool.command)
            for definition in self.arguments[:index]:
                if "=" in definition:
                    variable, value = definition.split("=", 1)
                    try:
                        self.environment_validator(definition)
                    except ValidationError:
                        self.logger.warning(
                            f"[Security] Refused to set sensitive environment variable '{variable}' from execution arguments"
                        )
                        continue
                    variable = variable.strip()
                    # The quotes only group the value in the command template, so the tool
                    # must receive the value without them
                    value = value.strip().replace("'", "").replace('"', "")
                    environment[variable] = value
                    self.hashable_environment[variable] = value
            self.arguments = self.arguments[index:]
        settings = Settings.objects.first()
        for proxy in model_to_dict(Settings).keys():
            if "_proxy" in proxy and getattr(settings, proxy) is not None:
                environment[proxy.upper()] = getattr(settings, proxy)
        return environment

    def before_running(self) -> None:
        """Prepare whatever the tool needs before being run.

        The tools that don't declare a directory to run in are given a writable one,
        so the executors that override this hook have to call it or the tools that
        write relative to their working directory would do it wherever Rekono runs
        from.
        """
        if self.execution_directory:
            return
        self.temporary_execution_directory = CONFIG.reports / str(uuid.uuid4())
        self.temporary_execution_directory.mkdir(parents=True, exist_ok=True)
        self.execution_directory = self.temporary_execution_directory

    def run_tool(self, environment: dict[str, Any] = os.environ.copy()) -> None:  # pragma: no cover
        """Run the tool and save its output in the execution.

        The execution is marked as failed if the tool returns an error code, unless
        the tool reports errors that aren't errors, like finding nothing.

        Args:
            environment: Environment variables to run the tool with.
        """
        self.logger.info(f"[Tool] Running: {self.mask_sensitive_data(' '.join(self.arguments))}")
        # The tools that don't write the report themselves write it to the standard output
        stdout = (
            self.report
            if self.execution.configuration.tool.output_format
            and not any([str(self.report) in arg for arg in self.arguments])
            else None
        )
        if stdout:
            with self.report.open("w") as _stdout:
                # Stderr is discarded as the stdout file will be used as stdout
                # and report, so stderr content would break the report format
                process = subprocess.run(self.arguments, stdout=_stdout, env=environment, cwd=self.execution_directory)
            output = ""
            if self.report.is_file():
                with self.report.open("r") as _output:
                    output = _output.read()
        else:
            process = subprocess.run(
                self.arguments,
                env=environment,
                cwd=self.execution_directory,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
            output = process.stdout
        if self.execution.configuration.tool.output_format and self.report.is_file():
            self.execution.output_file = self.report
        # The colors of the output are removed, so the parsers and the users read the same
        self.execution.output_plain = self.mask_sensitive_data(
            re.sub(r"(\x9B|\x1B\[)[\d]*[ -\/]*[@-~]", "", output, flags=re.IGNORECASE)
        )
        self.execution.save(update_fields=["output_plain", "output_file"])
        if not self.execution.configuration.tool.ignore_exit_code and process.returncode > 0:
            self.execution.error()

    def after_running(self) -> None:
        """Process whatever the tool leaves behind after being run.

        The working directory is removed with everything that the tool wrote in it,
        unless the tool was already installed in it, so the executors that override
        this hook have to call it after taking what they need from that directory.
        """
        if self.temporary_execution_directory and self.temporary_execution_directory.is_dir():
            shutil.rmtree(self.temporary_execution_directory, ignore_errors=True)
        self.temporary_execution_directory = None

    def mask_sensitive_data(self, value: str | None, wordlists: list[Wordlist] = []) -> str | None:
        """Remove the authentication secrets and the Rekono paths from a text.

        Args:
            value: Text that the users will read, like the command of the execution,
              the output of the tool, or its report.
            wordlists: Wordlists that the execution used, needed to hide the ones
              that are stored outside the Rekono wordlists directory.

        Returns:
            The text with every secret and token of the target masked, even the ones
            that are part of a bigger value like a header or a Basic token, the
            report replaced by a generic output name, the script of the tool and the
            wordlists replaced by their file names, and the Rekono directories
            removed from the rest of the paths. An empty text is returned as it is.
        """
        if not value:
            return value
        for authentication in Authentication.objects.filter(target_port__target=self.execution.task.target).all():
            for secret in (authentication.secret, authentication.token):
                if secret:
                    value = value.replace(secret, "*" * len(secret))
        if self.report:
            value = value.replace(
                str(self.report), f"output.{self.execution.configuration.tool.output_format or 'txt'}"
            )
        for wordlist in wordlists:
            value = value.replace(wordlist.path, Path(wordlist.path).name)
        if self.execution.configuration.tool.script and self.execution.configuration.tool.script_directory_property:
            value = value.replace(
                str(
                    Path(getattr(CONFIG, self.execution.configuration.tool.script_directory_property.lower()))
                    / self.execution.configuration.tool.script
                ),
                self.execution.configuration.tool.script,
            )
        # The Rekono directories are removed last, because the paths replaced above
        # wouldn't match anymore once their directory is out of the text
        for directory in [CONFIG.wordlists, CONFIG.reports]:
            value = value.replace(f"{directory}/", "").replace(str(directory), "")
        return value

    def execute(
        self,
        findings: list[Finding],
        target_ports: list[TargetPort],
        input_vulnerabilities: list[InputVulnerability],
        input_technologies: list[InputTechnology],
        wordlists: list[Wordlist],
    ) -> None:
        """Run the whole execution, from building the command to processing the output.

        The execution is skipped if the tool isn't installed or if the available
        data can't fill its required arguments, and it's marked as failed if
        anything goes wrong while the tool runs.

        Args:
            findings: Findings that the previous executions discovered.
            target_ports: Ports that the target defines.
            input_vulnerabilities: Vulnerabilities that the users provided.
            input_technologies: Technologies that the users provided.
            wordlists: Wordlists that the task uses.
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
        # The command is saved before running the tool, so the users can see what is running
        self.execution.executed_command = self.mask_sensitive_data(" ".join(self.arguments))
        self.execution.save(update_fields=["executed_command"])
        self.before_running()
        try:
            # The tests exercise the whole lifecycle without running the real tools
            if not CONFIG.testing:
                self.run_tool(self.environment)
        except (RuntimeError, Exception) as ex:
            self.logger.error(f"[Tool] {self.execution.configuration.tool.name} execution crashed: {str(ex)}")
            self.execution.error()
        finally:
            self.after_running()
