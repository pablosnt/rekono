from django_filters.filters import ModelChoiceFilter
from findings.models import OSINT
from framework.filters import MultipleFieldFilterSet
from projects.models import Project
from targets.models import Target
from tasks.models import Task
from tools.models import Tool
from users.models import User


class FindingFilter(MultipleFieldFilterSet):
    tool = ModelChoiceFilter(
        queryset=Tool.objects.all(), field_name="executions__configuration__tool"
    )
    task = ModelChoiceFilter(queryset=Task.objects.all(), field_name="executions__task")
    target = ModelChoiceFilter(
        queryset=Target.objects.all(), field_name="executions__task__target"
    )
    project = ModelChoiceFilter(
        queryset=Project.objects.all(), field_name="executions__task__target__project"
    )
    executor = ModelChoiceFilter(
        queryset=User.objects.all(), field_name="executions__task__executor"
    )

    class Meta:
        model = OSINT  # It's needed to define a non-abstract model as default. It will be overwritten
        fields = {
            "executions": ["exact"],
            "triage_status": ["exact"],
            "triage_comment": ["exact", "icontains"],
        }
