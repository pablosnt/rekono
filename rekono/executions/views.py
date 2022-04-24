from django.db.models import QuerySet
from executions.filters import ExecutionFilter
from executions.models import Execution
from executions.serializers import ExecutionSerializer
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet

# Create your views here.


class ExecutionViewSet(GenericViewSet, ListModelMixin, RetrieveModelMixin):
    '''Execution ViewSet that includes: get and retrieve features.'''

    queryset = Execution.objects.all().order_by('-id')
    serializer_class = ExecutionSerializer
    filterset_class = ExecutionFilter
    # Fields used to search executions
    search_fields = ['task__target__target', 'tool__name', 'configuration__name']

    def get_queryset(self) -> QuerySet:
        '''Get the Execution queryset that the user is allowed to get, based on project members.

        Returns:
            QuerySet: Execution queryset
        '''
        queryset = super().get_queryset()
        return queryset.filter(task__target__project__members=self.request.user)
