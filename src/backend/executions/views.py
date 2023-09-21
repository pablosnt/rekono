from executions.filters import ExecutionFilter
from executions.models import Execution
from executions.serializers import ExecutionSerializer
from framework.views import BaseViewSet

# Create your views here.


class ExecutionViewSet(BaseViewSet):
    queryset = Execution.objects.all()
    serializer_class = ExecutionSerializer
    filterset_class = ExecutionFilter
    search_fields = [
        "task__target__target",
        "task__process__name",
        "configuration__tool__name",
        "configuration__name",
    ]
    ordering_fields = [
        "id",
        "task",
        "group",
        "configuration",
        "configuration__tool",
        "creation",
        "enqueued_at",
        "start",
        "end",
    ]
    http_method_names = [
        "get",
    ]
