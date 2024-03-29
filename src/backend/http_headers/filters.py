from django_filters.filters import ModelChoiceFilter
from django_filters.rest_framework import FilterSet
from http_headers.models import HttpHeader
from projects.models import Project


class HttpHeaderFilter(FilterSet):
    project = ModelChoiceFilter(
        queryset=Project.objects.all(), field_name="target__project"
    )

    class Meta:
        model = HttpHeader
        fields = {
            "target": ["exact", "isnull"],
            "user": ["exact", "isnull"],
            "key": ["exact", "icontains"],
            "value": ["exact", "icontains"],
        }
