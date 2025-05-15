from framework.models import BaseInput
from projects.models import Project

# Create your models here.


class InputParameter(BaseInput):
    project_field = "tasks__target__project"

    class Meta:
        abstract = True

    def get_project(self) -> list[Project]:
        return [task.get_project() for task in self.tasks.all()]
