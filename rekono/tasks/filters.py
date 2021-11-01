from django_filters import rest_framework
from django_filters.rest_framework.filters import OrderingFilter
from tasks.models import Task


class TaskFilter(rest_framework.FilterSet):
    o = OrderingFilter(
        fields=(
            ('target__project', 'project'),
            'target', 'process', 'tool', 'intensity', 'executor', 'status', 'start', 'end'
        ),
    )

    class Meta:
        model = Task
        fields = {
            'target': ['exact'],
            'target__project': ['exact'],
            'process': ['exact'],
            'tool': ['exact'],
            'intensity': ['exact'],
            'executor': ['exact'],
            'status': ['exact'],
            'start': ['gte', 'lte', 'exact'],
            'end': ['gte', 'lte', 'exact']
        }
