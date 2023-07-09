import base64
from typing import Any, Dict

from django.db import models
from input_types.enums import InputKeyword
from input_types.models import BaseInput
from projects.models import Project
from security.input_validation import validate_credential, validate_name
from targets.models import TargetPort
from tools.models import Input

from authentications.enums import AuthenticationType

# Create your models here.


class Authentication(models.Model, BaseInput):
    '''Authentication model.'''

    # Related target port
    target_port = models.OneToOneField(TargetPort, related_name='authentication', on_delete=models.CASCADE)
    name = models.TextField(max_length=100, validators=[validate_name])         # Credential name
    credential = models.TextField(max_length=500, validators=[validate_credential])     # Credential value
    type = models.TextField(max_length=8, choices=AuthenticationType.choices)   # Authentication type

    def filter(self, input: Input) -> bool:
        '''Check if this instance is valid based on input filter.

        Args:
            input (Input): Tool input whose filter will be applied

        Returns:
            bool: Indicate if this instance match the input filter or not
        '''
        if input.filter and input.filter[0] == '!':                             # Negative filter
            return self.type.lower() not in input.filter[1:].split(',')         # Check if filter doesn't match the type
        # Check if filter matches the type
        return not input.filter or self.type.lower() in input.filter.lower().split(',')

    def parse(self, accumulated: Dict[str, Any] = {}) -> Dict[str, Any]:
        '''Get useful information from this instance to be used in tool execution as argument.

        Args:
            accumulated (Dict[str, Any], optional): Information from other instances of the same type. Defaults to {}.

        Returns:
            Dict[str, Any]: Useful information for tool executions, including accumulated if setted
        '''
        output = self.target_port.parse()
        credential = {
            InputKeyword.USERNAME.name.lower(): self.name if self.type == AuthenticationType.BASIC else None,
            InputKeyword.COOKIE_NAME.name.lower(): self.name if self.type == AuthenticationType.COOKIE else None,
            InputKeyword.SECRET.name.lower(): self.credential,
            InputKeyword.TOKEN.name.lower(): self.credential if self.type != AuthenticationType.BASIC else base64.b64encode(f'{self.name}:{self.credential}'.encode()).decode(),  # noqa: E501
            InputKeyword.CREDENTIAL_TYPE.name.lower(): self.type,
            InputKeyword.CREDENTIAL_TYPE_LOWER.name.lower(): self.type.lower(),
        }
        output.update(credential)
        return output

    def __str__(self) -> str:
        '''Instance representation in text format.

        Returns:
            str: String value that identifies this instance
        '''
        return f'{self.target_port.__str__()} - {self.name}'

    def get_project(self) -> Project:
        '''Get the related project for the instance. This will be used for authorization purposes.

        Returns:
            Project: Related project entity
        '''
        return self.target_port.target.project
