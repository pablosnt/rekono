"""Base model of the input parameters."""

from functools import cached_property

from framework.models import BaseInput
from projects.models import Project


class InputParameter(BaseInput):
    """Base data that the users provide as input for the tools.

    The parameters aren't created inside a project, they are linked to the tasks
    that use them, so the same parameter can be reused by tasks of any project.
    """

    _project_field = "tasks__target__project"

    class Meta:
        """Model configuration, marking it as abstract."""

        abstract = True

    @cached_property
    def parent_project(self) -> list[Project]:
        """The projects of the tasks that use this parameter."""
        return [task.parent_project for task in self.tasks.all()]
