"""Base filter classes for findings framework REST API.

Provides foundational filter classes including FindingFilter and
TriageFindingFilter that all specific finding filters inherit from
with standardized filtering capabilities for execution context and status tracking.
"""

from django_filters.filters import ModelMultipleChoiceFilter

from findings.models import OSINT
from framework.filters import MultipleFieldFilterSet
from projects.models import Project
from targets.models import Target
from tasks.models import Task
from tools.models import Tool
from users.models import User


class FindingFilter(MultipleFieldFilterSet):
    """Base filter for all finding types with execution context.

    Provides standardized filtering capabilities for finding data including
    tool, task, target, project, and executor relationships with fixing
    status and DefectDojo integration filtering.

    Attributes:
        tool (ModelMultipleChoiceFilter): Filter by tools used in executions
        task (ModelMultipleChoiceFilter): Filter by tasks that produced findings
        target (ModelMultipleChoiceFilter): Filter by targets in execution context
        project (ModelMultipleChoiceFilter): Filter by projects containing findings
        executor (ModelMultipleChoiceFilter): Filter by users who executed tasks
    """

    tool = ModelMultipleChoiceFilter(queryset=Tool.objects.all(), field_name="executions__configuration__tool")
    task = ModelMultipleChoiceFilter(queryset=Task.objects.all(), field_name="executions__task")
    target = ModelMultipleChoiceFilter(queryset=Target.objects.all(), field_name="executions__task__target")
    project = ModelMultipleChoiceFilter(queryset=Project.objects.all(), field_name="executions__task__target__project")
    executor = ModelMultipleChoiceFilter(queryset=User.objects.all(), field_name="executions__task__executor")

    class Meta:
        """Meta configuration for FindingFilter.

        Defines model reference and filterable fields for base finding filtering.
        Uses OSINT as the default model reference which is overridden by subclasses.

        Attributes:
            model (type): Default model class (overridden by subclasses)
            fields (dict): Field names mapped to available lookup types
        """

        model = OSINT  # It's needed to define a non-abstract model as default. It will be overwritten
        fields = {
            "executions": ["exact"],
            "is_fixed": ["exact"],
            "auto_fixed": ["exact"],
            "fixed_date": ["gte", "lte", "exact"],
            "fixed_by": ["exact"],
            "defectdojo_id": ["exact"],
            "created_from_user_input": ["exact"],
        }


class TriageFindingFilter(FindingFilter):
    """Base filter for findings requiring triage workflow.

    Extends FindingFilter to add triage-specific filtering capabilities
    including status classification, comments, dates, and user attribution
    for comprehensive triage management.
    """

    class Meta:
        """Meta configuration for TriageFindingFilter.

        Extends FindingFilter.Meta to include triage-specific filtering fields
        for comprehensive triage workflow management.

        Attributes:
            model (type): Default model class (OSINT, overridden by subclasses)
            fields (dict): Field names mapped to available lookup types including triage fields
        """

        model = OSINT
        fields = {
            **FindingFilter.Meta.fields.copy(),
            "triage_status": ["exact", "in"],
            "triage_comment": ["exact", "icontains"],
            "triage_date": ["gte", "lte", "exact"],
            "triage_by": ["exact"],
        }
