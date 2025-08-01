"""Filters for the notes app.

This module provides Django REST Framework filters for the Note model,
enabling advanced query filtering and search capabilities for note data
with complex relationship-based filtering.
"""

from django_filters.filters import BooleanFilter, CharFilter

from framework.filters import LikeFilter, MultipleFieldFilterSet, MultipleNumberFilter
from notes.models import Note


class NoteFilter(LikeFilter, MultipleFieldFilterSet):
    """FilterSet for the Note model with advanced relationship filtering.

    This filter set provides comprehensive filtering capabilities for Note
    instances through the API. It supports filtering by direct fields as well
    as complex relationship-based filtering that can traverse multiple model
    relationships to find notes based on related entities.

    Attributes:
        related_target: Filter notes by target relationships through multiple paths.
        related_task: Filter notes by task relationships through multiple paths.
        tag: Filter notes by tag names.
        is_fork: Filter notes that are forks (have a forked_from relationship).
    """

    # Complex filter that searches for notes related to a target through
    # multiple relationship paths, including indirect relationships through
    # executions and tasks
    related_target = MultipleNumberFilter(
        fields=[
            "target",
            "task__target",
            "osint__executions__task__target",
            "host__executions__task__target",
            "port__executions__task__target",
            "path__executions__task__target",
            "credential__executions__task__target",
            "technology__executions__task__target",
            "vulnerability__executions__task__target",
            "exploit__executions__task__target",
        ]
    )

    # Complex filter that searches for notes related to a task through
    # multiple relationship paths, including indirect relationships through
    # executions
    related_task = MultipleNumberFilter(
        fields=[
            "task",
            "osint__executions__task",
            "host__executions__task",
            "port__executions__task",
            "path__executions__task",
            "credential__executions__task",
            "technology__executions__task",
            "vulnerability__executions__task",
            "exploit__executions__task",
        ]
    )

    # Filter notes by tag names
    tag = CharFilter(field_name="tags__name")

    # Filter notes that are forks (have a forked_from relationship)
    # This uses a reverse lookup to find notes that are forks of other notes
    is_fork = BooleanFilter(field_name="forked_from", lookup_expr="isnull", exclude=True)

    class Meta:
        """Meta configuration for the NoteFilter.

        This inner class defines the filter's configuration, specifying
        which model to filter and which fields support which types of
        filtering operations.

        Attributes:
            model: The Django model class to filter (Note).
            fields: Dictionary mapping field names to list of filter types.
        """

        model = Note
        fields = {
            "project": ["exact"],
            "target": ["exact"],
            "task": ["exact"],
            "execution": ["exact"],
            "osint": ["exact"],
            "host": ["exact"],
            "port": ["exact"],
            "path": ["exact"],
            "credential": ["exact"],
            "technology": ["exact"],
            "vulnerability": ["exact"],
            "exploit": ["exact"],
            "title": ["exact", "icontains"],
            "body": ["icontains"],
            "owner": ["exact"],
            "public": ["exact"],
            "forked_from": ["exact"],
            "created_at": ["gte", "lte", "exact"],
            "updated_at": ["gte", "lte", "exact"],
        }
