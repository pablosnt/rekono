from functools import cached_property

from framework.models import BaseInput
from projects.models import Project

# Create your models here.


class InputParameter(BaseInput):
    _project_field = "tasks__target__project"

    class Meta:
        abstract = True

    @cached_property
    def parent_project(self) -> list[Project]:
        return [task.parent_project for task in self.tasks.all()]
