"""Django models for security tools management and configuration.

Defines comprehensive data models for security tool management including tool
definitions, configurations, arguments, inputs, and outputs. Models support
dynamic tool discovery, installation validation, version detection, and
flexible configuration management for automated security testing workflows.

Key Components:
    Tool: Core security tool definitions with installation status and version tracking
    Configuration: Stage-based tool execution configurations with customizable arguments
    Argument: Tool parameter definitions with input type mapping and validation rules
    Input: Input type associations for tool arguments with filtering and ordering
    Output: Expected output types from tool configurations for workflow chaining
    Intensity: Tool execution intensity levels with performance and thoroughness control

Architecture:
    The models use a hierarchical relationship structure where tools contain multiple
    configurations, which define arguments that accept various input types. This design
    enables flexible tool parameter generation and automated workflow orchestration
    based on available inputs and desired outputs.
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
    """Model representing a security testing tool with installation and version tracking.

    Represents individual security tools integrated into Rekono with comprehensive
    metadata, installation status validation, version detection, and dynamic class
    loading for tool-specific executors and parsers. Supports both command-line
    tools and script-based tools with configurable execution environments.

    Attributes:
        name (TextField): Unique tool identifier and display name (max 30 chars)
        command (TextField): System command or executable name (max 30 chars)
        script (TextField): Optional script filename for script-based tools (max 100 chars)
        script_directory_property (TextField): CONFIG property for script location (max 100 chars)
        run_directory_property (TextField): CONFIG property for execution directory (max 100 chars)
        ignore_exit_code (BooleanField): Whether to ignore non-zero exit codes
        is_installed (BooleanField): Current installation status of the tool
        version (TextField): Detected version string (max 100 chars)
        version_argument (TextField): Command argument to retrieve version (max 30 chars)
        output_format (TextField): Expected output file format (max 5 chars)
        reference (TextField): Documentation or homepage URL (max 250 chars)
        icon (TextField): Tool icon or logo URL (max 250 chars)
        defectdojo_scan_type (TextField): DefectDojo integration scan type (max 100 chars)

    Example:
        Create a new security tool:

        ```python
        tool = Tool.objects.create(
            name="Nmap",
            command="nmap",
            version_argument="--version",
            output_format="xml"
        )
        tool.update_status()  # Check installation and version
        ```
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
        """Get the related class for tool-specific functionality.

        Dynamically imports and returns tool-specific executor or parser classes
        based on the tool name and package. Falls back to base classes when
        tool-specific implementations are not available.

        Args:
            package (str): Package path for the class type (e.g., "tools.parsers")
            name (str): Tool name to construct the module and class names

        Returns:
            Any: The tool-specific class or base class if specific implementation not found
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
        """Get the parser class for this tool.

        Returns the tool-specific parser class for processing output files and
        extracting security findings. Uses cached property for performance.

        Returns:
            Any: Tool-specific parser class or BaseParser if specific implementation not found
        """
        return self._get_related_class("tools.parsers", self.name)

    @cached_property
    def executor_class(self) -> Any:
        """Get the executor class for this tool.

        Returns the tool-specific executor class for handling command construction
        and execution logic. Uses cached property for performance.

        Returns:
            Any: Tool-specific executor class or BaseExecutor if specific implementation not found
        """
        return self._get_related_class("tools.executors", self.name)

    def update_status(self) -> None:
        """Update the installation status and version information for this tool.

        Checks if the tool is currently installed on the system and attempts to
        detect the version if available. Updates the database with current status.
        """
        self.is_installed = self._is_installed()
        self.version = self._parse_version() if self.is_installed else None
        self.save(update_fields=["is_installed", "version"])

    def _is_installed(self) -> bool:
        """Check if the tool is installed and available for execution.

        Validates tool availability by checking command accessibility and script
        file existence based on tool configuration.

        Returns:
            bool: True if the tool is installed and available, False otherwise
        """
        if self.command and not shutil.which(self.command):
            return False
        if self.script_directory_property:
            path = Path(getattr(CONFIG, self.script_directory_property.lower()))
            if not path.is_dir() or not (path / self.script).is_file():
                return False
        return True  # pragma: no cover

    def _parse_version(self) -> str | None:  # pragma: no cover
        """Parse version information from the tool's version output.

        Executes the tool with version argument and extracts version string using
        regex pattern matching.

        Returns:
            str | None: Parsed version string or None if version cannot be determined
        """
        version_regex = r"(?!m)[a-z]?[\d]+\.[\d]+\.?[\d]*-?[a-z]*"
        if self.version_argument:
            process = subprocess.run(
                [i for i in [self.command, self.script, self.version_argument] if i],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
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
        """Return string representation of the tool.

        Returns:
            str: The tool name
        """
        return self.name


class Intensity(BaseModel):
    """Model representing execution intensity levels for security tools.

    Defines intensity configurations that control tool execution thoroughness
    and performance characteristics. Each tool can have multiple intensity
    levels with associated command arguments for different scanning approaches.

    Attributes:
        tool (ForeignKey): The associated Tool instance
        argument (TextField): Command argument for this intensity level (max 50 chars)
        value (IntegerField): Intensity level from IntensityEnum (QUIET, NORMAL, AGGRESSIVE)

    Example:
        Create intensity configuration:

        ```python
        intensity = Intensity.objects.create(
            tool=nmap_tool,
            argument="-T4",
            value=IntensityEnum.HARD
        )
        ```
    """

    tool = models.ForeignKey(Tool, related_name="intensities", on_delete=models.CASCADE)
    argument = models.TextField(max_length=50, default="", blank=True)
    value = models.IntegerField(choices=IntensityEnum.choices, default=IntensityEnum.NORMAL)

    def __str__(self) -> str:
        """Return string representation of the intensity configuration.

        Returns:
            str: String in format "tool_name - intensity_level"
        """
        return f"{self.tool.__str__()} - {IntensityEnum(self.value).name}"


class Configuration(BaseModel):
    """Model representing tool execution configurations for different stages.

    Defines specific configurations for tool execution with stage-based parameters,
    custom command template, and default selection logic. Configurations determine how
    tools are executed within security testing workflows.

    Attributes:
        name (TextField): Configuration identifier and display name (max 30 chars)
        tool (ForeignKey): The associated Tool instance
        command_template (TextField): Command template with placeholders (max 250 chars)
        stage (IntegerField): Execution stage from Stage enum
        default (BooleanField): Whether this is the default configuration for the tool
        default_scanned_port (IntegerField): Default port to scan (0-65535, optional)

    Example:
        Create a tool configuration:

        ```python
        config = Configuration.objects.create(
            name="Full Scan",
            tool=nmap_tool,
            command_template="-sS -O",
            stage=Stage.RECON,
            default=True
        )
        ```
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
        """Meta configuration for the Configuration model.

        Attributes:
            constraints (list): Database constraints ensuring tool-name uniqueness
        """

        constraints = [models.UniqueConstraint(fields=["tool", "name"], name="unique_configuration")]

    def __str__(self) -> str:
        """Return string representation of the configuration.

        Returns:
            str: String in format "tool_name - configuration_name"
        """
        return f"{self.tool.__str__()} - {self.name}"


class Argument(BaseModel):
    """Model representing configuration command-line arguments and their specifications.

    Defines individual arguments that configurations accept, including parameter names,
    command-line flags, requirement status, and multiplicity support. Arguments
    are mapped to input types for automated parameter generation.

    Attributes:
        configuration (ForeignKey): The associated Configuration instance
        name (TextField): Argument identifier and display name (max 20 chars)
        argument (TextField): Command-line flag or parameter (max 50 chars)
        required (BooleanField): Whether this argument is mandatory for configuration execution
        multiple (BooleanField): Whether multiple input values are accepted

    Example:
        Create a configuration argument:

        ```python
        argument = Argument.objects.create(
            configuration=nmap_config,
            name="target",
            argument="",
            required=True,
            multiple=True
        )
        ```
    """

    configuration = models.ForeignKey(
        Configuration, related_name="arguments", on_delete=models.CASCADE, blank=True, null=True
    )
    name = models.TextField(max_length=20)
    argument = models.TextField(max_length=50, default="", blank=True)
    required = models.BooleanField(default=False)
    # Indicates if multiple BaseInputs are accepted
    multiple = models.BooleanField(default=False)

    class Meta:
        """Meta configuration for the Argument model.

        Attributes:
            constraints (list): Database constraints ensuring configuration-name argument uniqueness
        """

        constraints = [models.UniqueConstraint(fields=["configuration", "name"], name="unique_argument")]

    def __str__(self) -> str:
        """Return string representation of the argument.

        Returns:
            str: String in format "configuration_name - argument_name"
        """
        return f"{self.configuration.__str__()} - {self.name}"


class Input(BaseModel):
    """Model representing input type associations for tool arguments.

    Links tool arguments to specific input types with optional filtering and
    ordering specifications. Enables automated parameter generation based on
    available inputs and their types.

    Attributes:
        argument (ForeignKey): The associated Argument instance
        type (ForeignKey): The InputType that this argument accepts
        filter (TextField): Optional filter expression for input selection (max 250 chars)
        order (IntegerField): Processing order for multiple inputs

    Example:
        Create an input type mapping:

        ```python
        input_mapping = Input.objects.create(
            argument=target_argument,
            type=host_input_type,
            filter="status=active",
            order=1
        )
        ```
    """

    argument = models.ForeignKey(Argument, related_name="inputs", on_delete=models.CASCADE)
    type = models.ForeignKey(InputType, related_name="inputs", on_delete=models.CASCADE)
    filter = models.TextField(max_length=250, blank=True, null=True)
    order = models.IntegerField(default=1)

    class Meta:
        """Meta configuration for the Input model.

        Attributes:
            constraints (list): Database constraints ensuring argument-order input uniqueness
        """

        constraints = [models.UniqueConstraint(fields=["argument", "order"], name="unique_input")]

    def __str__(self) -> str:
        """Return string representation of the input mapping.

        Returns:
            str: String in format "argument - input_type"
        """
        return f"{self.argument.__str__()} - {self.type.__str__()}"


class Output(BaseModel):
    """Model representing expected output types from tool configurations.

    Defines the types of data that tool configurations produce as output,
    enabling workflow chaining where tool outputs become inputs for subsequent
    tools in security testing processes.

    Attributes:
        configuration (ForeignKey): The associated Configuration instance
        type (ForeignKey): The InputType that this configuration produces as output

    Example:
        Create an output type specification:

        ```python
        output = Output.objects.create(
            configuration=nmap_config,
            type=port_input_type
        )
        ```
    """

    configuration = models.ForeignKey(Configuration, related_name="outputs", on_delete=models.CASCADE)
    type = models.ForeignKey(InputType, related_name="outputs", on_delete=models.CASCADE)

    class Meta:
        """Meta configuration for the Output model.

        Attributes:
            constraints (list): Database constraints ensuring configuration-type output uniqueness
        """

        constraints = [models.UniqueConstraint(fields=["configuration", "type"], name="unique_output")]

    def __str__(self) -> str:
        """Return string representation of the output specification.

        Returns:
            str: String in format "configuration - output_type"
        """
        return f"{self.configuration.__str__()} - {self.type.__str__()}"
