from framework.views import BaseViewSet
from rest_framework.serializers import Serializer


class FindingViewSet(BaseViewSet):
    triage_serializer_class = None
    http_method_names = [
        "get",
        "put",
    ]

    def get_serializer_class(self) -> Serializer:
        if self.request.method == "PUT":
            return self.triage_serializer_class
        return super().get_serializer_class()
