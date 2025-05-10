from django_filters.filters import ModelChoiceFilter
from django_filters.rest_framework import FilterSet
from parameters.models import InputTechnology, InputVulnerability
from projects.models import Project
from targets.models import Target


class InputTechnologyFilter(FilterSet):
    """FilterSet to filter and sort input Technology entities."""

    project = ModelChoiceFilter(queryset=Project.objects.all(), field_name="task__target__project")
    target = ModelChoiceFilter(queryset=Target.objects.all(), field_name="task__targett")

    class Meta:
        model = InputTechnology
        fields = {
            "tasks": ["exact"],
            "name": ["exact", "icontains"],
            "version": ["exact", "icontains"],
        }


class InputVulnerabilityFilter(FilterSet):
    """FilterSet to filter and sort input Vulnerability entities."""

    project = ModelChoiceFilter(queryset=Project.objects.all(), field_name="tasks__target__project")
    target = ModelChoiceFilter(queryset=Target.objects.all(), field_name="tasks__targett")

    class Meta:
        model = InputVulnerability
        fields = {
            "tasks": ["exact"],
            "cve": ["exact"],
        }
