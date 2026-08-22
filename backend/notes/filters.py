"""Filters of the note endpoints.

Besides the thing that a note is directly about, the notes can be searched by the
findings around it, so asking for the notes of a host also returns the ones written
about its ports, its technologies, or its vulnerabilities.
"""

from django_filters.filters import BooleanFilter, CharFilter

from findings.models import Host, Port, Technology, Vulnerability
from framework.filters import LikeFilter, MultipleFieldFilterSet, MultipleModelFilter
from notes.models import Note
from targets.models import Target
from tasks.models import Task


class NoteFilter(LikeFilter, MultipleFieldFilterSet):
    """Filters to search the notes of a project.

    Attributes:
        related_target: Filter by a target, including the notes about its tasks and
          about the findings that those tasks discovered.
        related_task: Filter by a task, including the notes about the findings that
          it discovered.
        related_host: Filter by a host, including the notes about the findings
          discovered in its ports.
        related_port: Filter by a port, including the notes about the findings
          discovered in it.
        related_technology: Filter by a technology, including the notes about its
          credentials, vulnerabilities, and exploits.
        related_vulnerability: Filter by a vulnerability, including the notes about
          its exploits.
        tag: Filter by one of the tags of the note.
        is_fork: Filter the notes that are a copy of another one.
    """

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
    related_vulnerability = MultipleModelFilter(
        queryset=Vulnerability.objects.all(), fields=["vulnerability", "exploit__vulnerability"]
    )
    tag = CharFilter(field_name="tags__name")
    # exclude=True inverts the isnull lookup, so is_fork=True keeps the notes whose forked_from
    # is set instead of the ones whose forked_from is null
    is_fork = BooleanFilter(field_name="forked_from", lookup_expr="isnull", exclude=True)

    class Meta:
        """Filter configuration for the notes."""

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
