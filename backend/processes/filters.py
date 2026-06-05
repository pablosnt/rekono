"""Django filtering for process management queries.

Provides filter classes for process and step queries with advanced filtering
capabilities including tool-based filtering, stage filtering, and owner-based
filtering for comprehensive process discovery and management.
"""

from django_filters.filters import CharFilter, ChoiceFilter, ModelChoiceFilter
from django_filters.rest_framework import FilterSet

from framework.filters import LikeFilter
from processes.models import Process, Step
from tools.enums import Stage
from tools.models import Configuration, Tool
from users.models import User


class ProcessFilter(LikeFilter):
    """Filter class for Process model queries.

    Provides filtering capabilities for security testing processes including
    tool-based filtering, configuration filtering, and tag-based discovery
    with community features from LikeFilter.

    Attributes:
        configuration (ModelChoiceFilter): Filter by tool configuration used in process steps
        tool (ModelChoiceFilter): Filter by security tool used in process steps
        stage (ChoiceFilter): Filter by security testing stage (reconnaissance, enumeration, etc.)
        tag (CharFilter): Filter by process tags for categorization
        owner_username: Filter by owner username
    """

    configuration = ModelChoiceFilter(queryset=Configuration.objects.all(), field_name="steps__configuration")
    tool = ModelChoiceFilter(queryset=Tool.objects.all(), field_name="steps__configuration__tool")
    stage = ChoiceFilter(field_name="steps__configuration__stage", choices=Stage.choices)
    tag = CharFilter(field_name="tags__name")
    owner_username = CharFilter(field_name="owner__username", lookup_expr="icontains")

    class Meta:
        """Meta configuration for ProcessFilter.

        Defines the model and field-based filtering options for process queries.

        Attributes:
            model (Model): The Process model to filter
            fields (dict): Field-based filters with lookup types for name, description, and owner
        """

        model = Process
        fields = {
            "name": ["exact", "icontains"],
            "description": ["exact", "icontains"],
            "owner": ["exact"],
        }


class StepFilter(FilterSet):
    """Filter class for Step model queries.

    Provides filtering capabilities for process steps including owner-based
    filtering, tool-based filtering, and stage-based filtering for workflow
    step management and discovery.

    Attributes:
        owner (ModelChoiceFilter): Filter by process owner user
        tool (ModelChoiceFilter): Filter by security tool used in the step configuration
        stage (ChoiceFilter): Filter by security testing stage of the tool configuration
        tag (CharFilter): Filter by tool tags with inclusion matching
    """

    owner = ModelChoiceFilter(queryset=User.objects.all(), field_name="process__owner")
    tool = ModelChoiceFilter(queryset=Tool.objects.all(), field_name="configuration__tool")
    stage = ChoiceFilter(field_name="configuration__stage", choices=Stage.choices)
    tag = CharFilter(field_name="configuration__tool", lookup_expr="in")

    class Meta:
        """Meta configuration for StepFilter.

        Defines the model and field-based filtering options for step queries.

        Attributes:
            model (Model): The Step model to filter
            fields (dict): Field-based filters with exact lookup for process and configuration
        """

        model = Step
        fields = {"process": ["exact"], "configuration": ["exact"]}
