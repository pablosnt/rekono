import logging
from typing import Any, Dict, cast

from defectdojo.api import DefectDojo
from defectdojo.exceptions import DefectDojoException
from django.db import models
from input_types.base import BaseInput
from input_types.enums import InputKeyword
from input_types.utils import get_url
from projects.models import Project
from security.input_validation import validate_number
from tools.models import Input

from targets.enums import TargetType

# Create your models here.

logger = logging.getLogger()                                                    # Rekono logger


class Target(models.Model, BaseInput):
    '''Target model.'''

    project = models.ForeignKey(Project, related_name='targets', on_delete=models.CASCADE)      # Related project
    target = models.TextField(max_length=100)                                   # Target IP, domain or network
    type = models.TextField(max_length=10, choices=TargetType.choices)          # Target type
    # Related engagement Id in Defect-Dojo
    defectdojo_engagement_id = models.IntegerField(blank=True, null=True, validators=[validate_number])

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
            distinct = input.filter[0] == '!'
            filter_types = [
                cast(models.TextChoices, TargetType)[f.upper()] for f in input.filter.replace('!', '').split(',s')
            ]
            return self.type not in filter_types if distinct else self.type in filter_types
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

    def get_defectdojo_engagement(self, dd_client: DefectDojo) -> int:
        '''Get Id of the Defect-Dojo engagement associated to the target. If not exists, create a new one.

        Args:
            dd_client (DefectDojo): dd_client (DefectDojo): Defect-Dojo API client

        Returns:
            int: Engagement Id in Defect-Dojo
        '''
        exists = False
        if self.defectdojo_engagement_id is not None:
            exists, _ = dd_client.get_engagement(self.defectdojo_engagement_id)     # Check existing engagement Id
        if not exists:                                                          # Engagement not found
            self.create_defectdojo_engagement(dd_client)                        # Create a new engagement
        return self.defectdojo_engagement_id

    def create_defectdojo_engagement(self, dd_client: DefectDojo) -> None:
        '''Create Defect-Dojo engagement to import the executions and findings detected for the target.

        Args:
            dd_client (DefectDojo): Defect-Dojo API client
        '''
        # Create engagement in Defect-Dojo
        success, body = dd_client.create_engagement(
            self.project.defectdojo_product_id,
            self.target,
            f'Rekono assessment for {self.target}'
        )
        if success:
            logger.info(f'[Defect-Dojo] New engagement {body["id"]} related to target {self.id} has been created')
            self.defectdojo_engagement_id = body['id']                          # Save Defect-Dojo engagement Id
            self.save(update_fields=['defectdojo_engagement_id'])
        else:
            logger.warning(f"[Defect-Dojo] Engagement for the target {self.id} can't be created")
            raise DefectDojoException(
                {'engagement': [f"Defect-Dojo engagement related to target {self.id} can't be created"]}
            )


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
