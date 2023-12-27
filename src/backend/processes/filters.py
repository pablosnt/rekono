from django_filters.filters import CharFilter, ChoiceFilter, ModelChoiceFilter
from django_filters.rest_framework import FilterSet
from framework.filters import LikeFilter
from processes.models import Process, Step
from tools.models import Configuration, Tool
from users.models import User


class ProcessFilter(LikeFilter):
    configuration = ModelChoiceFilter(
        queryset=Configuration.objects.all(), field_name="steps__configuration"
    )
    tool = ModelChoiceFilter(
        queryset=Tool.objects.all(), field_name="steps__configuration__tool"
    )
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
    owner = ModelChoiceFilter(queryset=User.objects.all(), field_name="process__owner")
    tool = ModelChoiceFilter(
        queryset=Tool.objects.all(), field_name="configuration__tool"
    )
    stage = ChoiceFilter(field_name="configuration__stage")
    tag = CharFilter(field_name="configuration__tool", lookup_expr="in")

    class Meta:
        model = Step
        fields = {
            "process": ["exact"],
            "configuration": ["exact"],
        }
