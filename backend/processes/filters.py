"""Filters of the process and step endpoints."""

from django_filters.filters import CharFilter, ChoiceFilter, ModelChoiceFilter
from django_filters.rest_framework import FilterSet

from framework.filters import LikeFilter
from processes.models import Process, Step
from tools.enums import Stage
from tools.models import Configuration, Tool
from users.models import User


class ProcessFilter(LikeFilter):
    """Filters to search processes, also by the tools that their steps execute.

    Attributes:
        configuration: Filter by a tool configuration used by one of the steps.
        tool: Filter by a tool used by one of the steps.
        stage: Filter by the stage of the tools used by the steps.
        tag: Filter by one of the tags of the process.
        owner_username: Filter by the username of the owner.
    """

    configuration = ModelChoiceFilter(queryset=Configuration.objects.all(), field_name="steps__configuration")
    tool = ModelChoiceFilter(queryset=Tool.objects.all(), field_name="steps__configuration__tool")
    stage = ChoiceFilter(field_name="steps__configuration__stage", choices=Stage.choices)
    tag = CharFilter(field_name="tags__name")
    owner_username = CharFilter(field_name="owner__username", lookup_expr="icontains")

    class Meta:
        """Filter configuration for the processes."""

        model = Process
        fields = {
            "name": ["exact", "icontains"],
            "description": ["exact", "icontains"],
            "owner": ["exact"],
        }


class StepFilter(FilterSet):
    """Filters to search steps by their process and by the tool that they execute.

    Attributes:
        owner: Filter by the owner of the process that contains the step.
        tool: Filter by the tool that the step executes.
        stage: Filter by the stage of that tool.
        tag: Filter by several tools at once.
    """

    owner = ModelChoiceFilter(queryset=User.objects.all(), field_name="process__owner")
    tool = ModelChoiceFilter(queryset=Tool.objects.all(), field_name="configuration__tool")
    stage = ChoiceFilter(field_name="configuration__stage", choices=Stage.choices)
    tag = CharFilter(field_name="configuration__tool", lookup_expr="in")

    class Meta:
        """Filter configuration for the steps."""

        model = Step
        fields = {"process": ["exact"], "configuration": ["exact"]}
