from django_filters.filters import ModelMultipleChoiceFilter
from findings.models import OSINT
from framework.filters import MultipleFieldFilterSet
from projects.models import Project
from targets.models import Target
from tasks.models import Task
from tools.models import Tool
from users.models import User


class FindingFilter(MultipleFieldFilterSet):
    tool = ModelMultipleChoiceFilter(queryset=Tool.objects.all(), field_name="executions__configuration__tool")
    task = ModelMultipleChoiceFilter(queryset=Task.objects.all(), field_name="executions__task")
    target = ModelMultipleChoiceFilter(queryset=Target.objects.all(), field_name="executions__task__target")
    project = ModelMultipleChoiceFilter(queryset=Project.objects.all(), field_name="executions__task__target__project")
    executor = ModelMultipleChoiceFilter(queryset=User.objects.all(), field_name="executions__task__executor")

    class Meta:
        model = OSINT  # It's needed to define a non-abstract model as default. It will be overwritten
        fields = {
            "executions": ["exact"],
            "is_fixed": ["exact"],
            "auto_fixed": ["exact"],
            "fixed_date": ["gte", "lte", "exact"],
            "fixed_by": ["exact"],
        }


class TriageFindingFilter(FindingFilter):
    class Meta:
        model = OSINT
        fields = {
            **FindingFilter.Meta.fields.copy(),
            "triage_status": ["exact", "in"],
            "triage_comment": ["exact", "icontains"],
            "triage_date": ["gte", "lte", "exact"],
            "triage_by": ["exact"],
        }
