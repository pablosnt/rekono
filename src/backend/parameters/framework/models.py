from framework.models import BaseInput
from projects.models import Project

# Create your models here.


class InputParameter(BaseInput):
    class Meta:
        abstract = True

    def get_project(self) -> list[Project]:
        return [task.get_project() for task in self.tasks.all()]

    # TODO: Move to an attribute?
    @classmethod
    def get_project_field(cls) -> str:
        return "tasks__target__project"
