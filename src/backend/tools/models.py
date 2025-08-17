import importlib
import re
import shutil
import subprocess
from functools import cached_property
from pathlib import Path
from typing import Any

from django.db import models

from framework.models import BaseLike, BaseModel
from input_types.models import InputType
from rekono.settings import CONFIG
from tools.enums import Intensity as IntensityEnum
from tools.enums import Stage


class Tool(BaseLike):
    name = models.TextField(max_length=30, unique=True)
    command = models.TextField(max_length=30)
    script = models.TextField(max_length=100, blank=True, null=True)
    # TODO: lower these default values in the fixtures
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
        return self._get_related_class("tools.parsers", self.name)

    @cached_property
    def executor_class(self) -> Any:
        return self._get_related_class("tools.executors", self.name)

    def update_status(self) -> None:
        self.is_installed = self._is_installed()
        self.version = self._parse_version() if self.is_installed else None
        self.save(update_fields=["is_installed", "version"])

    def _is_installed(self) -> bool:
        if self.command and not shutil.which(self.command):
            return False
        if self.script_directory_property:
            path = Path(getattr(CONFIG, self.script_directory_property.lower()))
            if not path.is_dir() or not (path / self.script).is_file():
                return False
        return True

    def _parse_version(self) -> str | None:
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
        return None

    def __str__(self) -> str:
        return self.name


class Intensity(BaseModel):
    tool = models.ForeignKey(Tool, related_name="intensities", on_delete=models.CASCADE)
    argument = models.TextField(max_length=50, default="", blank=True)
    value = models.IntegerField(choices=IntensityEnum.choices, default=IntensityEnum.NORMAL)

    def __str__(self) -> str:
        return f"{self.tool.__str__()} - {IntensityEnum(self.value).name}"


class Configuration(BaseModel):
    name = models.TextField(max_length=30)
    tool = models.ForeignKey(Tool, related_name="configurations", on_delete=models.CASCADE)
    arguments = models.TextField(max_length=250, default="", blank=True)
    stage = models.IntegerField(choices=Stage.choices)
    default = models.BooleanField(default=False)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["tool", "name"], name="unique_configuration")]

    def __str__(self) -> str:
        return f"{self.tool.__str__()} - {self.name}"


class Argument(BaseModel):
    tool = models.ForeignKey(Tool, related_name="arguments", on_delete=models.CASCADE)
    name = models.TextField(max_length=20)
    argument = models.TextField(max_length=50, default="", blank=True)
    required = models.BooleanField(default=False)
    # Indicates if multiple BaseInputs are accepted
    multiple = models.BooleanField(default=False)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["tool", "name"], name="unique_argument")]

    def __str__(self) -> str:
        return f"{self.tool.__str__()} - {self.name}"


class Input(BaseModel):
    argument = models.ForeignKey(Argument, related_name="inputs", on_delete=models.CASCADE)
    type = models.ForeignKey(InputType, related_name="inputs", on_delete=models.CASCADE)
    filter = models.TextField(max_length=250, blank=True, null=True)
    order = models.IntegerField(default=1)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["argument", "order"], name="unique_input")]

    def __str__(self) -> str:
        return f"{self.argument.__str__()} - {self.type.__str__()}"


class Output(BaseModel):
    configuration = models.ForeignKey(Configuration, related_name="outputs", on_delete=models.CASCADE)
    type = models.ForeignKey(InputType, related_name="outputs", on_delete=models.CASCADE)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["configuration", "type"], name="unique_output")]

    def __str__(self) -> str:
        return f"{self.configuration.__str__()} - {self.type.__str__()}"
