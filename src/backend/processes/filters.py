from django_filters.rest_framework import FilterSet
from framework.filters import LikeFilter
from processes.models import Process, Step


class ProcessFilter(LikeFilter):
    class Meta:
        model = Process
        fields = {
            "name": ["exact", "icontains"],
            "description": ["exact", "icontains"],
            "owner": ["exact"],
            "owner__username": ["exact", "icontains"],
            "steps__configuration": ["exact"],
            "steps__configuration__name": ["exact", "icontains"],
            "steps__configuration__stage": ["exact"],
            "steps__configuration__tool": ["exact"],
            "steps__configuration__tool__name": ["exact", "icontains"],
            "tags__name": ["in"],
        }


class StepFilter(FilterSet):
    class Meta:
        model = Step
        fields = {
            "process": ["exact"],
            "process__name": ["exact", "icontains"],
            "process__description": ["exact", "icontains"],
            "process__owner": ["exact"],
            "process__tags__name": ["in"],
            "configuration": ["exact"],
            "configuration__name": ["exact", "icontains"],
            "configuration__stage": ["exact"],
            "configuration__tool": ["exact"],
            "configuration__tool__name": ["exact", "icontains"],
        }
