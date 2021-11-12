from django_filters.rest_framework.filters import OrderingFilter
from executions.models import Execution

from rekono.api.filters import ToolFilter


class ExecutionFilter(ToolFilter):
    tool_fields = ('task__tool', 'step__tool')
    o = OrderingFilter(
        fields=(
            ('task__target', 'target'),
            ('task__target__project', 'project'),
            ('task__process', 'process'),
            ('task__intensity', 'intensity'),
            ('task__executor', 'executor'),
            ('step__tool', 'step__tool'),
            ('task__tool', 'task__tool'),
            'status',
            'start',
            'end'
        ),
    )

    class Meta:
        model = Execution
        fields = {
            'task': ['exact'],
            'task__target': ['exact'],
            'task__target__project': ['exact'],
            'task__process': ['exact'],
            'task__intensity': ['exact'],
            'task__executor': ['exact'],
            'status': ['exact'],
            'start': ['gte', 'lte', 'exact'],
            'end': ['gte', 'lte', 'exact']
        }
