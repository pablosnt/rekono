"""Django filters for notes REST API endpoints.

Provides advanced filtering capabilities for note API queries including
complex relationship filters, tag-based filtering, and fork detection.
"""

from django_filters.filters import BooleanFilter, CharFilter

from framework.filters import LikeFilter, MultipleFieldFilterSet, MultipleNumberFilter
from notes.models import Note


class NoteFilter(LikeFilter, MultipleFieldFilterSet):
    """Filter class for Note model queries with advanced relationship filtering.

    Provides filtering options for note API endpoints with support for complex
    relationship queries, tag filtering, and fork detection capabilities.

    Attributes:
        related_target (MultipleNumberFilter): Complex target relationship filter
        related_task (MultipleNumberFilter): Complex task relationship filter
        tag (CharFilter): Tag name filter
        is_fork (BooleanFilter): Fork detection filter
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

        Attributes:
            model (Model): The Note model to filter
            fields (dict): Field names and their supported filter operations
        """

        model = Note
        fields = {
            "project": ["exact"],
            "target": ["exact"],
            "task": ["exact"],
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
