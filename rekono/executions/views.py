from api.views import GetViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin

from executions.filters import ExecutionFilter
from executions.models import Execution
from executions.serializers import ExecutionSerializer

# Create your views here.


class ExecutionViewSet(GetViewSet, ListModelMixin, RetrieveModelMixin):
    '''Execution ViewSet that includes: get and retrieve features.'''

    queryset = Execution.objects.all().order_by('-id')
    serializer_class = ExecutionSerializer
    filterset_class = ExecutionFilter
    # Fields used to search executions
    search_fields = ['task__target__target', 'tool__name', 'configuration__name']
    members_field = 'task__target__project__members'
