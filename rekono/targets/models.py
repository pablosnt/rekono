from typing import Any, Dict, cast

from django.db import models
from input_types.base import BaseInput
from input_types.enums import InputKeyword
from input_types.utils import get_url
from projects.models import Project
from security.input_validation import validate_endpoint, validate_number
from targets.enums import TargetType
from tools.models import Input

# Create your models here.


class Target(models.Model, BaseInput):
    '''Target model.'''

    project = models.ForeignKey(Project, related_name='targets', on_delete=models.CASCADE)      # Related project
    target = models.TextField(max_length=100)                                   # Target IP, domain or network
    type = models.TextField(max_length=10, choices=TargetType.choices)          # Target type

    class Meta:
        '''Model metadata.'''

        constraints = [
            # Unique constraint by: Project and Target
            models.UniqueConstraint(fields=['project', 'target'], name='unique target')
        ]

    def filter(self, input: Input) -> bool:
        '''Check if this instance is valid based on input filter.

        Args:
            input (Input): Tool input whose filter will be applied

        Returns:
            bool: Indicate if this instance match the input filter or not
        '''
        if not input.filter:
            return True
        try:
            return cast(models.TextChoices, TargetType)[input.filter] == self.type
        except KeyError:
            return True

    def parse(self, accumulated: Dict[str, Any] = {}) -> Dict[str, Any]:
        '''Get useful information from this instance to be used in tool execution as argument.

        Args:
            accumulated (Dict[str, Any], optional): Information from other instances of the same type. Defaults to {}.

        Returns:
            Dict[str, Any]: Useful information for tool executions, including accumulated if setted
        '''
        return {
            InputKeyword.TARGET.name.lower(): self.target,
            InputKeyword.HOST.name.lower(): self.target,
            InputKeyword.URL.name.lower(): get_url(self.target)
        }

    def __str__(self) -> str:
        '''Instance representation in text format.

        Returns:
            str: String value that identifies this instance
        '''
        return self.target

    def get_project(self) -> Project:
        '''Get the related project for the instance. This will be used for authorization purposes.

        Returns:
            Project: Related project entity
        '''
        return self.project


class TargetPort(models.Model, BaseInput):
    '''Target port model.'''

    target = models.ForeignKey(Target, related_name='target_ports', on_delete=models.CASCADE)       # Related target
    port = models.IntegerField(validators=[validate_number])                    # Port number

    class Meta:
        '''Model metadata.'''

        constraints = [
            # Unique constraint by: Target and Port
            models.UniqueConstraint(fields=['target', 'port'], name='unique target port')
        ]

    def filter(self, input: Input) -> bool:
        '''Check if this instance is valid based on input filter.

        Args:
            input (Input): Tool input whose filter will be applied

        Returns:
            bool: Indicate if this instance match the input filter or not
        '''
        if not input.filter:
            return True
        try:
            to_check = int(input.filter)
            # If the filter is a number, target ports will be filtered by port
            return to_check == self.port
        except ValueError:
            return True

    def parse(self, accumulated: Dict[str, Any] = {}) -> Dict[str, Any]:
        '''Get useful information from this instance to be used in tool execution as argument.

        Args:
            accumulated (Dict[str, Any], optional): Information from other instances of the same type. Defaults to {}.

        Returns:
            Dict[str, Any]: Useful information for tool executions, including accumulated if setted
        '''
        output = {
            InputKeyword.TARGET.name.lower(): self.target.target,
            InputKeyword.HOST.name.lower(): self.target.target,
            InputKeyword.PORT.name.lower(): self.port,
            InputKeyword.PORTS.name.lower(): [self.port],
            InputKeyword.URL.name.lower(): get_url(self.target.target, self.port)
        }
        if accumulated and InputKeyword.PORTS.name.lower() in accumulated:
            output[InputKeyword.PORTS.name.lower()] = accumulated[InputKeyword.PORTS.name.lower()]
            output[InputKeyword.PORTS.name.lower()].append(self.port)
        output[InputKeyword.PORTS_COMMAS.name.lower()] = ','.join([str(port) for port in output[InputKeyword.PORTS.name.lower()]])    # noqa: E501
        return output

    def __str__(self) -> str:
        '''Instance representation in text format.

        Returns:
            str: String value that identifies this instance
        '''
        return f'{self.target.target} - {self.port}'

    def get_project(self) -> Project:
        '''Get the related project for the instance. This will be used for authorization purposes.

        Returns:
            Project: Related project entity
        '''
        return self.target.project


class TargetEndpoint(models.Model, BaseInput):
    '''Target port model.'''

    # Related target port
    target_port = models.ForeignKey(TargetPort, related_name='target_endpoints', on_delete=models.CASCADE)
    endpoint = models.TextField(max_length=500, validators=[validate_endpoint])                     # Endpoint value

    class Meta:
        '''Model metadata.'''

        constraints = [
            # Unique constraint by: TargetPort and Endpoint
            models.UniqueConstraint(fields=['target_port', 'endpoint'], name='unique target endpoint')
        ]

    def filter(self, input: Input) -> bool:
        '''Check if this instance is valid based on input filter.

        Args:
            input (Input): Tool input whose filter will be applied

        Returns:
            bool: Indicate if this instance match the input filter or not
        '''
        if not input.filter:
            return True
        try:
            int(input.filter)
            # If the filter is a number, endpoint won't be filtered
            return True
        except ValueError:
            # If the filter is a string, endpoint will be filtered by endpoint
            return input.filter in self.endpoint

    def parse(self, accumulated: Dict[str, Any] = {}) -> Dict[str, Any]:
        '''Get useful information from this instance to be used in tool execution as argument.

        Args:
            accumulated (Dict[str, Any], optional): Information from other instances of the same type. Defaults to {}.

        Returns:
            Dict[str, Any]: Useful information for tool executions, including accumulated if setted
        '''
        output = self.target_port.parse()
        output[InputKeyword.URL.name.lower()] = get_url(
            self.target_port.target.target,
            self.target_port.port,
            self.endpoint
        )
        output[InputKeyword.ENDPOINT.name.lower()] = self.endpoint
        return output

    def __str__(self) -> str:
        '''Instance representation in text format.

        Returns:
            str: String value that identifies this instance
        '''
        return f'{self.target_port.__str__()} - {self.endpoint}'

    def get_project(self) -> Project:
        '''Get the related project for the instance. This will be used for authorization purposes.

        Returns:
            Project: Related project entity
        '''
        return self.target_port.target.project
