from framework.views import BaseViewSet
from target_ports.filters import TargetPortFilter
from target_ports.models import TargetPort
from target_ports.serializers import TargetPortSerializer

# Create your views here.


class TargetPortViewSet(BaseViewSet):
    """TargetPort ViewSet that includes: get, retrieve, create, and delete features."""

    queryset = TargetPort.objects.all()
    serializer_class = TargetPortSerializer
    filterset_class = TargetPortFilter
    # Fields used to search target ports
    search_fields = ["port", "path"]
    ordering_fields = ["id", "target", "port", "path"]
    http_method_names = [
        "get",
        "post",
        "delete",
    ]

    # # Project members field used for authorization purposes
    # members_field = "target__project__members"
