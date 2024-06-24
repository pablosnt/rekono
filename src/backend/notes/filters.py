from django_filters.filters import BooleanFilter, CharFilter
from framework.filters import LikeFilter, MultipleFieldFilterSet
from notes.models import Note


class NoteFilter(LikeFilter, MultipleFieldFilterSet):
    tag = CharFilter(field_name="tags__name")
    is_fork = BooleanFilter(
        field_name="forked_from", lookup_expr="isnull", exclude=True
    )

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
