"""Models of the tools that Rekono runs and of what they can do.

A tool has one configuration per thing that it can do, each configuration declares
the arguments that its command accepts, and each argument declares the input types
that can fill it, so a command can be built from whatever the previous executions
discovered.
"""

import importlib
import re
import shutil
import subprocess
from functools import cached_property
from pathlib import Path
from typing import Any

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from framework.models import BaseLike, BaseModel
from input_types.models import InputType
from rekono.settings import CONFIG
from tools.enums import Intensity as IntensityEnum
from tools.enums import Stage


class Tool(BaseLike):
    """Security tool that Rekono can run.

    Attributes:
        name: Name of the tool, which also resolves its executor and its parser.
        command: Command that runs the tool.
        script: Script that the command runs, for the tools that aren't a command
          by themselves.
        script_directory_property: Configuration property with the directory where
          the script is installed.
        run_directory_property: Configuration property with the directory where the
          tool must be run.
        ignore_exit_code: Whether an execution succeeds even if the tool returns an
          error code, which some tools do when they find nothing.
        is_installed: Whether the tool is available in this deployment.
        version: Version of the tool that is installed.
        version_argument: Argument that makes the tool report its version.
        output_format: Extension of the file where the tool writes its results.
        reference: Link to the documentation of the tool.
        icon: Link to the logo of the tool.
        defectdojo_scan_type: Name that DefectDojo gives to the reports of this tool.
    """

    name = models.TextField(max_length=30, unique=True)
    command = models.TextField(max_length=30)
    script = models.TextField(max_length=100, blank=True, null=True)
    script_directory_property = models.TextField(max_length=100, blank=True, null=True)
    run_directory_property = models.TextField(max_length=100, blank=True, null=True)
    ignore_exit_code = models.BooleanField(default=False)
    is_installed = models.BooleanField(default=False)
    version = models.TextField(max_length=100, blank=True, null=True)
    version_argument = models.TextField(max_length=30, blank=True, null=True)
    output_format = models.TextField(max_length=5, blank=True, null=True)
    reference = models.TextField(max_length=250, blank=True, null=True)
    icon = models.TextField(max_length=250, blank=True, null=True)
    defectdojo_scan_type = models.TextField(max_length=100, blank=True, null=True)

    def _get_related_class(self, package: str, name: str) -> Any:
        """Get the executor or the parser class that belongs to a tool.

        Args:
            package: Package where the class is searched, which is tools.executors
              or tools.parsers.
            name: Name of the tool, from which the module and the class names are
              built.

        Returns:
            The class of the tool, or the base one if the tool doesn't need
            anything special, which is the case for most of them.
        """
        try:
            # nosemgrep: python.lang.security.audit.non-literal-import.non-literal-import
            module = importlib.import_module(f"{package.lower()}.{name.lower().replace(' ', '_').replace('-', '_')}")
            cls = getattr(
                module,
                name[0].upper() + name[1:].lower().replace(" ", "").replace("-", ""),
            )
        except (AttributeError, ModuleNotFoundError):
            # nosemgrep: python.lang.security.audit.non-literal-import.non-literal-import
            module = importlib.import_module(f"{package}.base")
            type = package.split(".")[-1][:-1]
            cls = getattr(module, f"Base{type[0].upper() + type[1:].lower()}")
        return cls

    @cached_property
    def parser_class(self) -> Any:
        """The class that turns the output of this tool into findings."""
        return self._get_related_class("tools.parsers", self.name)

    @cached_property
    def executor_class(self) -> Any:
        """The class that builds and runs the commands of this tool."""
        return self._get_related_class("tools.executors", self.name)

    def update_status(self) -> None:
        """Check if the tool is installed and which version it runs."""
        self.is_installed = self._is_installed()
        self.version = self._parse_version() if self.is_installed else None
        self.save(update_fields=["is_installed", "version"])

    def _is_installed(self) -> bool:
        """Check if the tool can be run in this deployment.

        Returns:
            Whether both the command and the script of the tool are available,
            skipping the check for the ones that the tool doesn't declare.
        """
        if self.command and not shutil.which(self.command):
            return False
        if self.script_directory_property:
            path = Path(getattr(CONFIG, self.script_directory_property.lower()))
            if not path.is_dir() or not (path / self.script).is_file():
                return False
        return True  # pragma: no cover

    def _parse_version(self) -> str | None:  # pragma: no cover
        """Get the version that the tool reports.

        Returns:
            The version, or None if the tool doesn't report one or if it fails,
            since the version is only informative.
        """
        version_regex = r"(?!m)[a-z]?[\d]+\.[\d]+\.?[\d]*-?[a-z]*"
        if self.version_argument:
            # The environment is the same one used to run the tool, so the tools that call a
            # bare python3 don't inherit the Rekono virtualenv and can find their dependencies
            process = subprocess.run(
                [i for i in [self.command, self.script, self.version_argument] if i],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                env=self.executor_class.get_clean_default_environment(),
                cwd=Path(getattr(CONFIG, self.script_directory_property.lower()))
                if self.script_directory_property
                else None,
            )
            if process.returncode == 0:
                version = re.search(
                    version_regex,
                    # zaproxy returns the Java version at the first line
                    re.sub(r"java version [^\s]*", "", process.stdout),
                    flags=re.IGNORECASE,
                )
                if version:
                    return version.group()

    def __str__(self) -> str:
        """Return the name of the tool."""
        return self.name


class Intensity(BaseModel):
    """Argument that a tool needs to be run with a given intensity.

    Attributes:
        tool: Tool that the intensity belongs to.
        argument: Argument that applies the intensity, which is empty for the tools
          whose default behavior already matches it.
        value: Intensity that the argument applies.
    """

    tool = models.ForeignKey(Tool, related_name="intensities", on_delete=models.CASCADE)
    argument = models.TextField(max_length=50, default="", blank=True)
    value = models.IntegerField(choices=IntensityEnum.choices, default=IntensityEnum.NORMAL)

    def __str__(self) -> str:
        """Return the tool and the intensity that the argument applies."""
        return f"{self.tool.__str__()} - {IntensityEnum(self.value).name}"


class Configuration(BaseModel):
    """One of the things that a tool can do, with the command that does it.

    Attributes:
        name: Name of the configuration, unique within its tool.
        tool: Tool that the configuration belongs to.
        command_template: Command of the tool, with the placeholders that the
          arguments fill.
        stage: Phase of the assessment where the configuration is run.
        default: Whether this is the configuration used when the users pick the
          tool without choosing one.
        default_scanned_port: Port that the configuration scans when the target
          doesn't define any.
        deprecated: Whether the configuration can still be used in new tasks and
          processes, since the old ones are kept for the executions that used them.
    """

    name = models.TextField(max_length=30)
    tool = models.ForeignKey(Tool, related_name="configurations", on_delete=models.CASCADE)
    command_template = models.TextField(max_length=250, default="", blank=True)
    stage = models.IntegerField(choices=Stage.choices)
    default = models.BooleanField(default=False)
    default_scanned_port = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(65535)], blank=True, null=True
    )
    deprecated = models.BooleanField(default=False)

    class Meta:
        """Model configuration, making the name unique within each tool."""

        constraints = [models.UniqueConstraint(fields=["tool", "name"], name="unique_configuration")]

    def __str__(self) -> str:
        """Return the tool and the name of the configuration."""
        return f"{self.tool.__str__()} - {self.name}"


class Argument(BaseModel):
    """Argument that a configuration accepts in its command.

    Attributes:
        configuration: Configuration that the argument belongs to.
        name: Name of the placeholder that the argument fills in the command.
        argument: Text added to the command, with the placeholders of the input
          data that fills it.
        required: Whether the configuration can't be run without this argument.
        multiple: Whether the argument accepts more than one input, so the tool
          scans everything at once instead of once per input.
    """

    configuration = models.ForeignKey(
        Configuration, related_name="arguments", on_delete=models.CASCADE, blank=True, null=True
    )
    name = models.TextField(max_length=20)
    argument = models.TextField(max_length=50, default="", blank=True)
    required = models.BooleanField(default=False)
    multiple = models.BooleanField(default=False)

    class Meta:
        """Model configuration, making the name unique within each configuration."""

        constraints = [models.UniqueConstraint(fields=["configuration", "name"], name="unique_argument")]

    def __str__(self) -> str:
        """Return the configuration and the name of the argument."""
        return f"{self.configuration.__str__()} - {self.name}"


class Input(BaseModel):
    """Kind of data that can fill an argument.

    Attributes:
        argument: Argument that this input can fill.
        type: Input type that the argument accepts.
        filter: Condition that the data must meet, like the service of a port.
        order: Position of this input among the ones of the argument, since the
          first one that has data available is the one used.
    """

    argument = models.ForeignKey(Argument, related_name="inputs", on_delete=models.CASCADE)
    type = models.ForeignKey(InputType, related_name="inputs", on_delete=models.CASCADE)
    filter = models.TextField(max_length=250, blank=True, null=True)
    order = models.IntegerField(default=1)

    class Meta:
        """Model configuration, making the order unique within each argument."""

        constraints = [models.UniqueConstraint(fields=["argument", "order"], name="unique_input")]

    def __str__(self) -> str:
        """Return the argument and the input type that can fill it."""
        return f"{self.argument.__str__()} - {self.type.__str__()}"


class Output(BaseModel):
    """Kind of finding that a configuration discovers.

    The outputs are what allows a process to chain its configurations, since a
    configuration can only run after the ones that produce the data that it needs.

    Attributes:
        configuration: Configuration that discovers this kind of finding.
        type: Input type that the configuration produces.
    """

    configuration = models.ForeignKey(Configuration, related_name="outputs", on_delete=models.CASCADE)
    type = models.ForeignKey(InputType, related_name="outputs", on_delete=models.CASCADE)

    class Meta:
        """Model configuration, allowing each type once per configuration."""

        constraints = [models.UniqueConstraint(fields=["configuration", "type"], name="unique_output")]

    def __str__(self) -> str:
        """Return the configuration and the input type that it produces."""
        return f"{self.configuration.__str__()} - {self.type.__str__()}"
