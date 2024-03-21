from django_filters.filters import BooleanFilter, CharFilter

from framework.filters import (
    LikeFilter,
    MultipleFieldFilterSet,
    MultipleModelChoiceFilter,
)
from notes.models import Note
from projects.models import Project


class NoteFilter(LikeFilter, MultipleFieldFilterSet):
    project = MultipleModelChoiceFilter(
        queryset=Project.objects.all(),
        field_name="id",
        fields=["project", "target__project"],
    )
    tag = CharFilter(field_name="tags__name", lookup_expr="in")
    is_fork = BooleanFilter(
        field_name="forked_from", lookup_expr="isnull", exclude=True
    )

    class Meta:
        model = Note
        fields = {
            "target": ["exact"],
            "title": ["exact", "icontains"],
            "body": ["icontains"],
            "owner": ["exact"],
            "public": ["exact"],
            "forked_from": ["exact"],
            "created_at": ["gte", "lte", "exact"],
            "updated_at": ["gte", "lte", "exact"],
        }
