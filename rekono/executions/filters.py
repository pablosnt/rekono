from api.filters import ToolFilter
from django_filters.rest_framework.filters import OrderingFilter
from executions.models import Execution


class ExecutionFilter(ToolFilter):
    '''FilterSet to filter and sort executions entities.'''

    tool_fields = ('task__tool', 'step__tool')                                  # Filter by two Tool fields
    o = OrderingFilter(                                                         # Ordering fields
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
        '''FilterSet metadata.'''

        model = Execution
        fields = {                                                              # Filter fields
            'task': ['exact'],
            'task__target': ['exact'],
            'task__target__target': ['exact', 'icontains'],
            'task__target__project': ['exact'],
            'task__target__project__name': ['exact', 'icontains'],
            'task__process': ['exact'],
            'task__intensity': ['exact'],
            'task__executor': ['exact'],
            'task__executor__username': ['exact', 'icontains'],
            'status': ['exact'],
            'start': ['gte', 'lte', 'exact'],
            'end': ['gte', 'lte', 'exact']
        }
