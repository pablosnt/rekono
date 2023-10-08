import importlib
import os
import re
import shutil
import subprocess
from typing import Any

from django.db import models
from framework.models import BaseLike, BaseModel
from input_types.models import InputType
from rekono.settings import CONFIG
from tools.enums import Intensity as IntensityEnum
from tools.enums import Stage

# Create your models here.


class Tool(BaseLike):
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

    def _get_tool_class(self, type: str) -> Any:
        try:
            # nosemgrep: python.lang.security.audit.non-literal-import.non-literal-import
            module = importlib.import_module(
                f'tools.{type.lower()}s.{self.name.lower().replace(" ", "_")}'
            )
            cls = getattr(
                module,
                self.name[0] + self.name[1:].replace(" ", ""),
            )
        except (AttributeError, ModuleNotFoundError):
            module = importlib.import_module(f"tools.{type.lower()}s.base")
            cls = getattr(module, f"Base{type[0].upper() + type[:1].lower()}")
        return cls

    def get_parser_class(self) -> Any:
        return self._get_tool_class("parser")

    def get_executor_class(self) -> Any:
        return self._get_tool_class("executor")

    def update_status(self) -> None:
        self.is_installed = (
            self.command
            and shutil.which(self.command) is not None
            and (
                (not self.script and not self.script_directory_property)
                or (
                    os.path.isdir(
                        getattr(CONFIG, self.script_directory_property.lower())
                    )
                    and os.path.isfile(
                        os.path.join(
                            getattr(CONFIG, self.script_directory_property.lower()),
                            self.script,
                        )
                    )
                )
            )
        )
        update_fields = ["is_installed"]
        if self.is_installed:
            self.version = self._parse_version()
            update_fields.append("version")
        self.save(update_fields=update_fields)

    def _parse_version(self) -> str:
        version_regex = r"(?!m)[a-z]?[\d]+\.[\d]+\.[\d]*-?[a-z]*"
        if self.version_argument:
            process = subprocess.run(
                [i for i in [self.command, self.script, self.version_argument] if i],
                capture_output=True,
            )
            if process.returncode == 0:
                output = (process.stdout or process.stderr).decode("utf-8").lower()
                version = re.search(
                    version_regex,
                    # zaproxy returns the Java version at the first line
                    re.sub("java version [^\s]*", "", output),
                )
                if version:
                    return version.group()

    def __str__(self) -> str:
        """Instance representation in text format.

        Returns:
            str: String value that identifies this instance
        """
        return self.name


class Intensity(BaseModel):
    tool = models.ForeignKey(Tool, related_name="intensities", on_delete=models.CASCADE)
    argument = models.TextField(max_length=50, default="", blank=True)
    value = models.IntegerField(
        choices=IntensityEnum.choices, default=IntensityEnum.NORMAL
    )

    def __str__(self) -> str:
        """Instance representation in text format.

        Returns:
            str: String value that identifies this instance
        """
        return f"{self.tool.name} - {IntensityEnum(self.value).name}"


class Configuration(BaseModel):
    name = models.TextField(max_length=30)
    tool = models.ForeignKey(
        Tool, related_name="configurations", on_delete=models.CASCADE
    )
    arguments = models.TextField(max_length=250, default="", blank=True)
    stage = models.IntegerField(choices=Stage.choices)
    default = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["tool", "name"], name="unique_configuration"
            )
        ]

    def __str__(self) -> str:
        """Instance representation in text format.

        Returns:
            str: String value that identifies this instance
        """
        return f"{self.tool.name} - {self.name}"


class Argument(BaseModel):
    tool = models.ForeignKey(Tool, related_name="arguments", on_delete=models.CASCADE)
    name = models.TextField(max_length=20)
    argument = models.TextField(max_length=50, default="", blank=True)
    required = models.BooleanField(default=False)
    multiple = models.BooleanField(default=False)  # Accepts multiple BaseInputs or not

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["tool", "name"], name="unique_argument")
        ]

    def __str__(self) -> str:
        """Instance representation in text format.

        Returns:
            str: String value that identifies this instance
        """
        return f"{self.tool.__str__()} - {self.name}"


class Input(models.Model):
    argument = models.ForeignKey(
        Argument, related_name="inputs", on_delete=models.CASCADE
    )
    type = models.ForeignKey(InputType, related_name="inputs", on_delete=models.CASCADE)
    filter = models.TextField(max_length=250, blank=True, null=True)
    order = models.IntegerField(default=1)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["argument", "order"], name="unique_input")
        ]

    def __str__(self) -> str:
        """Instance representation in text format.

        Returns:
            str: String value that identifies this instance
        """
        return f"{self.argument.__str__()} - {self.type.__str__()}"


class Output(models.Model):
    configuration = models.ForeignKey(
        Configuration, related_name="outputs", on_delete=models.CASCADE
    )
    type = models.ForeignKey(
        InputType, related_name="outputs", on_delete=models.CASCADE
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["configuration", "type"], name="unique_output"
            )
        ]

    def __str__(self) -> str:
        """Instance representation in text format.

        Returns:
            str: String value that identifies this instance
        """
        return f"{self.configuration.__str__()} - {self.type.__str__()}"
