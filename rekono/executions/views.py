from django.db.models import QuerySet
from executions.filters import ExecutionFilter
from executions.models import Execution
from executions.serializers import ExecutionSerializer
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin

# Create your views here.


class ExecutionViewSet(ListModelMixin, RetrieveModelMixin):
    '''Execution ViewSet that includes: get and retrieve features.'''

    queryset = Execution.objects.all().order_by('-id')
    serializer_class = ExecutionSerializer
    filterset_class = ExecutionFilter
    search_fields = [                                                           # Fields used to search executions
        'task__target__target', 'task__process__steps__tool__name',
        'task__process__steps__configuration__name', 'task__tool__name',
        'task__configuration__name'
    ]

    def get_queryset(self) -> QuerySet:
        '''Get the Execution queryset that the user is allowed to get, based on project members.

        Returns:
            QuerySet: Execution queryset
        '''
        queryset = super().get_queryset()
        return queryset.filter(task__target__project__members=self.request.user)
