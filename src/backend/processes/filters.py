from django_filters.filters import CharFilter, ChoiceFilter, ModelChoiceFilter
from django_filters.rest_framework import FilterSet
from framework.filters import LikeFilter
from processes.models import Process, Step


class ProcessFilter(LikeFilter):
    configuration = ModelChoiceFilter(field_name="steps__configuration")
    tool = ModelChoiceFilter(field_name="steps__configuration__tool")
    stage = ChoiceFilter(field_name="steps__configuration__stage")
    tag = CharFilter(field_name="tags__name", lookup_expr="in")

    class Meta:
        model = Process
        fields = {
            "name": ["exact", "icontains"],
            "description": ["exact", "icontains"],
            "owner": ["exact"],
        }


class StepFilter(FilterSet):
    owner = ModelChoiceFilter(field_name="process__owner")
    tool = ModelChoiceFilter(field_name="configuration__tool")
    stage = ChoiceFilter(field_name="configuration__stage")
    tag = CharFilter(field_name="configuration__tool", lookup_expr="in")

    class Meta:
        model = Step
        fields = {
            "process": ["exact"],
            "configuration": ["exact"],
        }
