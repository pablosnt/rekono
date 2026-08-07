"""Models of the processes and the steps that they are made of."""

from django.db import models
from taggit.managers import TaggableManager

from framework.models import BaseLike, BaseModel
from rekono.settings import AUTH_USER_MODEL
from security.validators.input_validator import Regex, Validator
from tools.models import Configuration


class Process(BaseLike):
    """Group of tool configurations that are executed together as one task.

    Attributes:
        name: Name of the process, unique in the whole platform.
        description: Description of what the process covers.
        owner: User that created the process, or None for the ones that Rekono
          provides by default.
        tags: Labels that the users assign to organize the processes.
    """

    name = models.TextField(max_length=100, unique=True, validators=[Validator(Regex.NAME, code="name")])
    description = models.TextField(max_length=500, validators=[Validator(Regex.TEXT, code="description")])
    owner = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    tags = TaggableManager()

    def __str__(self) -> str:
        """Return the name of the process."""
        return self.name


class Step(BaseModel):
    """Tool configuration that a process executes.

    The steps have no order of their own: the tasks decide when each one runs, from
    the stage of its tool and from the findings that the other steps report.

    Attributes:
        process: Process that this step belongs to.
        configuration: Tool configuration that the step executes.
    """

    process = models.ForeignKey(Process, related_name="steps", on_delete=models.CASCADE)
    configuration = models.ForeignKey(
        Configuration,
        related_name="steps",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    class Meta:
        """Model configuration, allowing each configuration once per process."""

        constraints = [models.UniqueConstraint(fields=["process", "configuration"], name="unique_step")]

    def __str__(self) -> str:
        """Return the process and the configuration of the step."""
        return f"{self.process.__str__()} - {self.configuration.__str__()}"
