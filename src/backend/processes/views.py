from framework.views import BaseViewSet, LikeViewSet
from processes.filters import ProcessFilter, StepFilter
from processes.models import Process, Step
from processes.serializers import ProcessSerializer, StepSerializer

# Create your views here.


class ProcessViewSet(LikeViewSet):
    queryset = Process.objects.all()
    serializer_class = ProcessSerializer
    filterset_class = ProcessFilter
    search_fields = ["name", "description"]
    ordering_fields = ["id", "name", "owner", "likes_count"]
    http_method_names = [
        "get",
        "post",
        "put",
        "delete",
    ]


class StepViewSet(BaseViewSet):
    queryset = Step.objects.all()
    serializer_class = StepSerializer
    filterset_class = StepFilter
    search_fields = [
        "process__name",
        "configuration__tool__name",
        "configuration__tool__command",
        "configuration__name",
    ]
    ordering_fields = ["id", "process", "configuration"]
    http_method_names = [
        "get",
        "post",
        "delete",
    ]
