from alerts.filters import AlertFilter
from alerts.models import Alert, MonitorSettings
from alerts.serializers import (
    AlertSerializer,
    EditAlertSerializer,
    MonitorSettingsSerializer,
)
from django.db.models import QuerySet
from drf_spectacular.utils import extend_schema
from framework.views import BaseViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from security.authorization.permissions import (
    OwnerPermission,
    ProjectMemberPermission,
    RekonoModelPermission,
)

# Create your views here.


class AlertViewSet(BaseViewSet):
    queryset = Alert.objects.all()
    serializer_class = AlertSerializer
    filterset_class = AlertFilter
    permission_classes = [
        IsAuthenticated,
        RekonoModelPermission,
        ProjectMemberPermission,
        OwnerPermission,
    ]
    search_fields = ["value"]
    ordering_fields = ["id", "item", "mode"]
    http_method_names = ["get", "post", "put", "delete"]

    def get_serializer_class(self) -> Serializer:
        return (
            EditAlertSerializer
            if self.request.method == "PUT"
            else super().get_serializer_class()
        )

    def get_queryset(self) -> QuerySet:
        queryset = super().get_queryset()
        return (
            queryset.filter(enabled=True).all()
            if self.request.method == "PUT"
            else queryset
        )

    @extend_schema(request=None, responses={204: None})
    @action(
        detail=True,
        methods=["POST", "DELETE"],
        permission_classes=[
            IsAuthenticated,
            RekonoModelPermission,
            ProjectMemberPermission,
        ],
    )
    def subscription(self, request: Request, pk: str) -> Response:
        alert = self.get_object()
        for method, expected_exists, error, operation in [
            (
                "POST",
                False,
                "You are already subscribed to this alert",
                alert.subscribers.add,
            ),
            (
                "DELETE",
                True,
                "You are already not subscribed to this alert",
                alert.subscribers.remove,
            ),
        ]:
            if request.method == method:
                if (
                    alert.subscribers.filter(id=request.user.id).exists()
                    is not expected_exists
                ):
                    return Response(
                        {"subscribe": error}, status=status.HTTP_400_BAD_REQUEST
                    )
                operation(request.user)
                break
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(request=None, responses={200: AlertSerializer})
    @action(detail=True, methods=["POST", "DELETE"])
    def enable(self, request: Request, pk: str) -> Response:
        alert = self.get_object()
        for method, new_value, operation in [
            ("POST", True, "enabled"),
            ("DELETE", False, "disabled"),
        ]:
            if request.method == method:
                if alert.enabled == new_value:
                    return Response(
                        {"enable": f"This alert is already {operation}"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                alert.enabled = new_value
                alert.save(update_fields=["enabled"])
                return Response(
                    AlertSerializer(alert, context={"request": request}).data,
                    status=status.HTTP_200_OK,
                )


class MonitorSettingsViewSet(BaseViewSet):
    queryset = MonitorSettings.objects.all()
    serializer_class = MonitorSettingsSerializer
    permission_classes = [IsAuthenticated, RekonoModelPermission]
    http_method_names = ["get", "put"]
