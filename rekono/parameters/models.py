from typing import Any, Dict, cast

from django.db import models
from findings.enums import Severity
from input_types.enums import InputKeyword
from input_types.models import BaseInput
from projects.models import Project
from security.input_validation import validate_cve, validate_name
from targets.models import Target
from tools.models import Input

# Create your models here.


class InputTechnology(models.Model, BaseInput):
    '''Input technology model.'''

    target = models.ForeignKey(Target, related_name='input_technologies', on_delete=models.CASCADE)     # Related target
    name = models.TextField(max_length=100, validators=[validate_name])         # Technology name
    version = models.TextField(max_length=100, validators=[validate_name], blank=True, null=True)   # Technology version

    class Meta:
        '''Model metadata.'''

        constraints = [
            # Unique constraint by: Target, Technology and Version
            models.UniqueConstraint(fields=['target', 'name', 'version'], name='unique input technology')
        ]

    def filter(self, input: Input) -> bool:
        '''Check if this instance is valid based on input filter.

        Args:
            input (Input): Tool input whose filter will be applied

        Returns:
            bool: Indicate if this instance match the input filter or not
        '''
        return not input.filter or input.filter.lower() in self.name.lower()

    def parse(self, accumulated: Dict[str, Any] = {}) -> Dict[str, Any]:
        '''Get useful information from this instance to be used in tool execution as argument.

        Args:
            accumulated (Dict[str, Any], optional): Information from other instances of the same type. Defaults to {}.

        Returns:
            Dict[str, Any]: Useful information for tool executions, including accumulated if setted
        '''
        output = self.target.parse()
        output[InputKeyword.TECHNOLOGY.name.lower()] = self.name
        if self.version:
            output[InputKeyword.VERSION.name.lower()] = self.version
        return output

    def __str__(self) -> str:
        '''Instance representation in text format.

        Returns:
            str: String value that identifies this instance
        '''
        base = f'{self.target.__str__()} - {self.name}'
        return f'{base} - {self.version}' if self.version else base

    def get_project(self) -> Project:
        '''Get the related project for the instance. This will be used for authorization purposes.

        Returns:
            Project: Related project entity
        '''
        return self.target.project


class InputVulnerability(models.Model, BaseInput):
    '''Input vulnerability model.'''

    target = models.ForeignKey(Target, related_name='input_vulnerabilities', on_delete=models.CASCADE)  # Related target
    cve = models.TextField(max_length=20, validators=[validate_cve])            # CVE

    class Meta:
        '''Model metadata.'''

        constraints = [
            # Unique constraint by: Target and CVE
            models.UniqueConstraint(fields=['target', 'cve'], name='unique input vulnerability')
        ]

    def filter(self, input: Input) -> bool:
        '''Check if this instance is valid based on input filter.

        Args:
            input (Input): Tool input whose filter will be applied

        Returns:
            bool: Indicate if this instance match the input filter or not
        '''
        return (
            not input.filter or
            input.filter.capitalize() in cast(models.TextChoices, Severity) or
            input.filter.lower().startswith('cwe-') or
            input.filter.lower() == 'cve' or
            (input.filter.lower().startswith('cve-') and input.filter.lower() == self.cve.lower())
        )

    def parse(self, accumulated: Dict[str, Any] = {}) -> Dict[str, Any]:
        '''Get useful information from this instance to be used in tool execution as argument.

        Args:
            accumulated (Dict[str, Any], optional): Information from other instances of the same type. Defaults to {}.

        Returns:
            Dict[str, Any]: Useful information for tool executions, including accumulated if setted
        '''
        output = self.target.parse()
        output[InputKeyword.CVE.name.lower()] = self.cve
        return output

    def __str__(self) -> str:
        '''Instance representation in text format.

        Returns:
            str: String value that identifies this instance
        '''
        return f'{self.target.__str__()} - {self.cve}'

    def get_project(self) -> Project:
        '''Get the related project for the instance. This will be used for authorization purposes.

        Returns:
            Project: Related project entity
        '''
        return self.target.project
