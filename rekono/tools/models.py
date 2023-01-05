from django.db import models
from input_types.models import InputType
from likes.models import LikeBase

from tools.enums import IntensityRank, Stage

# Create your models here.


class Tool(LikeBase):
    '''Tool model.'''

    name = models.TextField(max_length=30, unique=True)                         # Tool name
    command = models.TextField(max_length=30, blank=True, null=True)            # Tool command
    output_format = models.TextField(max_length=5, blank=True, null=True)       # Tool output file format
    defectdojo_scan_type = models.TextField(max_length=50, blank=True, null=True)   # Related Defect-Dojo scan type
    reference = models.TextField(max_length=250, blank=True, null=True)         # Tool reference link
    icon = models.TextField(max_length=250, blank=True, null=True)              # Tool icon link

    def __str__(self) -> str:
        '''Instance representation in text format.

        Returns:
            str: String value that identifies this instance
        '''
        return self.name


class Intensity(models.Model):
    '''Intensity model.'''

    tool = models.ForeignKey(Tool, related_name='intensities', on_delete=models.CASCADE)            # Related tool
    argument = models.TextField(max_length=50, default='', blank=True)          # Argument needed to apply the intensity
    value = models.IntegerField(choices=IntensityRank.choices, default=IntensityRank.NORMAL)        # Intensity value

    def __str__(self) -> str:
        '''Instance representation in text format.

        Returns:
            str: String value that identifies this instance
        '''
        return f'{self.tool.name} - {IntensityRank(self.value).name}'


class Configuration(models.Model):
    '''Configuration model.'''

    name = models.TextField(max_length=30)                                      # Configuration name
    tool = models.ForeignKey(Tool, related_name='configurations', on_delete=models.CASCADE)         # Related tool
    arguments = models.TextField(max_length=250, default='', blank=True)
    stage = models.IntegerField(choices=Stage.choices)                          # Related pentesting stage
    default = models.BooleanField(default=False)                                # Indicate if it's default configuration

    class Meta:
        '''Model metadata.'''

        constraints = [
            # Unique constraint by: Tool and Name
            models.UniqueConstraint(fields=['tool', 'name'], name='unique configuration')
        ]

    def __str__(self) -> str:
        '''Instance representation in text format.

        Returns:
            str: String value that identifies this instance
        '''
        return f'{self.tool.name} - {self.name}'


class Argument(models.Model):
    '''Argument model.'''

    tool = models.ForeignKey(Tool, related_name='arguments', on_delete=models.CASCADE)              # Related tool
    name = models.TextField(max_length=20)                                      # Argument name
    argument = models.TextField(max_length=50, default='', blank=True)          # Argument value
    required = models.BooleanField(default=False)                               # Indicate if it's required argument
    multiple = models.BooleanField(default=False)                               # Accepts multiple BaseInputs or not

    class Meta:
        '''Model metadata.'''

        constraints = [
            # Unique constraint by: Tool and Name
            models.UniqueConstraint(fields=['tool', 'name'], name='unique argument')
        ]

    def __str__(self) -> str:
        '''Instance representation in text format.

        Returns:
            str: String value that identifies this instance
        '''
        return f'{self.tool.__str__()} - {self.name}'


class Input(models.Model):
    '''Input model.'''

    argument = models.ForeignKey(Argument, related_name='inputs', on_delete=models.CASCADE)         # Related argument
    type = models.ForeignKey(InputType, related_name='inputs', on_delete=models.CASCADE)            # Related input type
    filter = models.TextField(max_length=250, blank=True, null=True)            # Filter to apply to BaseInputs
    order = models.IntegerField(default=1)                                      # Preference order

    class Meta:
        '''Model metadata.'''

        constraints = [
            # Unique constraint by: Argument and Order
            models.UniqueConstraint(fields=['argument', 'order'], name='unique input')
        ]

    def __str__(self) -> str:
        '''Instance representation in text format.

        Returns:
            str: String value that identifies this instance
        '''
        return f'{self.argument.__str__()} - {self.type.__str__()}'


class Output(models.Model):
    '''Output model.'''

    # Related configuration
    configuration = models.ForeignKey(Configuration, related_name='outputs', on_delete=models.CASCADE)
    type = models.ForeignKey(InputType, related_name='outputs', on_delete=models.CASCADE)           # Related input type

    class Meta:
        '''Model metadata.'''

        constraints = [
            # Unique constraint by: Configuration and Input Type
            models.UniqueConstraint(fields=['configuration', 'type'], name='unique output')
        ]

    def __str__(self) -> str:
        '''Instance representation in text format.

        Returns:
            str: String value that identifies this instance
        '''
        return f'{self.configuration.__str__()} - {self.type.__str__()}'
