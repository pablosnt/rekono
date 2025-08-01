"""Base filters for findings framework.

This module provides the foundational filter classes for the findings system,
including FindingFilter and TriageFindingFilter that all specific
finding filters inherit from. These provide standardized filtering
capabilities for finding data including execution context, fixing status,
and triage information.
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
    """Base filter for all finding types.

    Provides standardized filtering capabilities for finding data including
    tool, task, target, project, and executor information. All specific
    finding filters should inherit from this class.
    """

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
            "defectdojo_id": ["exact"],
        }


class TriageFindingFilter(FindingFilter):
    """Base filter for findings that require triage.

    Extends FindingFilter to add triage-specific filtering capabilities
    including triage status, comments, dates, and user information.
    """

    class Meta:
        model = OSINT
        fields = {
            **FindingFilter.Meta.fields.copy(),
            "triage_status": ["exact", "in"],
            "triage_comment": ["exact", "icontains"],
            "triage_date": ["gte", "lte", "exact"],
            "triage_by": ["exact"],
        }
