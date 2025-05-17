from django_filters.filters import BooleanFilter, CharFilter
from framework.filters import LikeFilter, MultipleFieldFilterSet, MultipleNumberFilter
from notes.models import Note


class NoteFilter(LikeFilter, MultipleFieldFilterSet):
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
    tag = CharFilter(field_name="tags__name")
    is_fork = BooleanFilter(field_name="forked_from", lookup_expr="isnull", exclude=True)

    class Meta:
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
