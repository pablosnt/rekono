"""Django filters for notes REST API endpoints.

Provides advanced filtering capabilities for note API queries including
complex relationship filters, tag-based filtering, and fork detection.
"""

from django_filters.filters import BooleanFilter, CharFilter

from findings.models import Host, Port, Technology, Vulnerability
from framework.filters import LikeFilter, MultipleFieldFilterSet, MultipleModelFilter
from notes.models import Note
from targets.models import Target
from tasks.models import Task


class NoteFilter(LikeFilter, MultipleFieldFilterSet):
    """Filter class for Note model queries with advanced relationship filtering.

    Provides filtering options for note API endpoints with support for complex
    relationship queries, tag filtering, and fork detection capabilities.

    Attributes:
        related_target (MultipleModelFilter): Complex target relationship filter covering
            direct target links and indirect paths through tasks and finding executions
        related_task (MultipleModelFilter): Complex task relationship filter covering
            direct task links and indirect paths through finding executions
        related_host (MultipleModelFilter): Complex host relationship filter covering
            direct host links and indirect paths through ports, paths, credentials,
            technologies, vulnerabilities, and exploits
        related_port (MultipleModelFilter): Complex port relationship filter covering
            direct port links and indirect paths through paths, credentials,
            technologies, vulnerabilities, and exploits
        related_technology (MultipleModelFilter): Complex technology relationship filter
            covering direct technology links and indirect paths through credentials,
            vulnerabilities, and exploits
        related_vulnerability (MultipleModelFilter): Complex vulnerability relationship
            filter covering direct vulnerability links and indirect paths through exploits
        tag (CharFilter): Tag name filter
        is_fork (BooleanFilter): Fork detection filter
    """

    # Complex filter that searches for notes related to a target through
    # multiple relationship paths, including indirect relationships through
    # executions and tasks
    related_target = MultipleModelFilter(
        queryset=Target.objects.all(),
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
        ],
    )
    # Complex filter that searches for notes related to a task through
    # multiple relationship paths, including indirect relationships through
    # executions
    related_task = MultipleModelFilter(
        queryset=Task.objects.all(),
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
        ],
    )
    # Complex filter that searches for notes related to a host through
    # multiple relationship paths, including indirect relationships through
    # ports, paths, credentials, technologies, vulnerabilities, and exploits
    related_host = MultipleModelFilter(
        queryset=Host.objects.all(),
        fields=[
            "host",
            "port__host",
            "path__port__host",
            "credential__technology__port__host",
            "technology__port__host",
            "vulnerability__port__host",
            "vulnerability__technology__port__host",
            "exploit__vulnerability__technology__port__host",
            "exploit__technology__port__host",
        ],
    )
    # Complex filter that searches for notes related to a port through
    # multiple relationship paths, including indirect relationships through
    # paths, credentials, technologies, vulnerabilities, and exploits
    related_port = MultipleModelFilter(
        queryset=Port.objects.all(),
        fields=[
            "port",
            "path__port",
            "credential__technology__port",
            "technology__port",
            "vulnerability__port",
            "vulnerability__technology__port",
            "exploit__vulnerability__technology__port",
            "exploit__technology__port",
        ],
    )
    # Complex filter that searches for notes related to a technology through
    # multiple relationship paths, including indirect relationships through
    # credentials, vulnerabilities and exploits
    related_technology = MultipleModelFilter(
        queryset=Technology.objects.all(),
        fields=[
            "technology",
            "credential__technology",
            "vulnerability__technology",
            "exploit__vulnerability__technology",
            "exploit__technology",
        ],
    )
    # Complex filter that searches for notes related to a vulnerability through
    # multiple relationship paths, including indirect relationships through exploits
    related_vulnerability = MultipleModelFilter(
        queryset=Vulnerability.objects.all(), fields=["vulnerability", "exploit__vulnerability"]
    )
    # Filter notes by tag names
    tag = CharFilter(field_name="tags__name")
    # Filter notes that are forks (have a forked_from relationship)
    # exclude=True inverts the isnull lookup, so is_fork=True keeps notes whose
    # forked_from is set rather than notes whose forked_from is null
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
