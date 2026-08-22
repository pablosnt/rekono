"""Base filters of the finding endpoints."""

from django_filters.filters import ModelMultipleChoiceFilter

from findings.models import OSINT
from framework.filters import MultipleFieldFilterSet
from projects.models import Project
from targets.models import Target
from tasks.models import Task
from tools.models import Tool
from users.models import User


class FindingFilter(MultipleFieldFilterSet):
    """Base filters to search findings by where they were discovered.

    Attributes:
        tool: Filter by a tool that discovered the finding.
        task: Filter by a task that discovered the finding.
        target: Filter by the target where the finding was discovered.
        project: Filter by the project that owns that target.
        executor: Filter by the user that created those tasks.
    """

    tool = ModelMultipleChoiceFilter(queryset=Tool.objects.all(), field_name="executions__configuration__tool")
    task = ModelMultipleChoiceFilter(queryset=Task.objects.all(), field_name="executions__task")
    target = ModelMultipleChoiceFilter(queryset=Target.objects.all(), field_name="executions__task__target")
    project = ModelMultipleChoiceFilter(queryset=Project.objects.all(), field_name="executions__task__target__project")
    executor = ModelMultipleChoiceFilter(queryset=User.objects.all(), field_name="executions__task__executor")

    class Meta:
        """Filter configuration shared by all the findings."""

        model = OSINT  # It's needed to define a non-abstract model as default. It will be overwritten
        fields = {
            "executions": ["exact"],
            "is_fixed": ["exact"],
            "auto_fixed": ["exact", "isnull"],
            "fixed_date": ["gte", "lte", "exact"],
            "fixed_by": ["exact"],
            "created_from_user_input": ["exact"],
        }


class TriageFindingFilter(FindingFilter):
    """Base filters of the findings that the auditors review one by one."""

    class Meta:
        """Filter configuration adding the triage fields to the common ones."""

        model = OSINT
        fields = {
            **FindingFilter.Meta.fields.copy(),
            "triage_status": ["exact", "in"],
            "triage_comment": ["exact", "icontains"],
            "triage_date": ["gte", "lte", "exact"],
            "triage_by": ["exact"],
        }
