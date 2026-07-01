"""Django REST framework views for alert management.

Provides REST API endpoints for managing alerts. Includes ViewSets for
CRUD operations and custom actions for subscription management and alert
enabling/disabling.
"""

from django.db.models import QuerySet
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from alerts.enums import AlertItem
from alerts.filters import AlertFilter
from alerts.models import Alert
from alerts.serializers import AlertSerializer, EditAlertSerializer
from framework.views import BaseViewSet
from security.authorization.permissions import (
    OwnerPermission,
    ProjectMemberPermission,
    RekonoModelPermission,
)


class AlertViewSet(BaseViewSet):
    """ViewSet for managing alert configurations.

    Provides REST API endpoints for alert CRUD operations plus custom actions
    for subscription management and enabling/disabling alerts.

    Custom Actions:
        subscription: Subscribe/unsubscribe users to alerts
        enable: Enable/disable specific alerts

    Attributes:
        queryset (QuerySet): All Alert objects
        serializer_class (Serializer): Default serializer for alert operations
        filterset_class (FilterSet): Filter class for querying alerts
        permission_classes (list): Required permissions for access
        search_fields (list): Fields that can be searched
        ordering_fields (list): Fields that can be used for ordering
    """

    queryset = Alert.objects.all()
    serializer_class = AlertSerializer
    filterset_class = AlertFilter
    permission_classes = [
        IsAuthenticated,
        RekonoModelPermission,
        ProjectMemberPermission,
        OwnerPermission,
    ]
    search_fields = ["item", "value"]
    ordering_fields = ["id", "project", "item", "owner"]

    def get_serializer_class(self) -> Serializer:
        """Get the appropriate serializer class based on the request method.

        Returns:
            Serializer: EditAlertSerializer for PUT requests, AlertSerializer otherwise
        """
        return EditAlertSerializer if self.request.method == "PUT" else super().get_serializer_class()

    def get_queryset(self) -> QuerySet:
        """Get the queryset for this view.

        For PUT requests, filters to only enabled alerts that support value updates.
        Otherwise returns all alerts.

        Returns:
            QuerySet: Filtered queryset based on request method
        """
        queryset = super().get_queryset()
        return (
            queryset.filter(
                enabled=True, item__in=[AlertItem.HOST, AlertItem.SERVICE, AlertItem.TECHNOLOGY, AlertItem.CVE]
            ).all()
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
        """Manage user subscription to an alert.

        POST: Subscribe the current user to the alert
        DELETE: Unsubscribe the current user from the alert

        Args:
            request (Request): The HTTP request object
            pk (str): Primary key of the alert

        Returns:
            Response: HTTP 204 on success, HTTP 400 with error message on failure
        """
        alert = self.get_object()
        is_subscribed = alert.subscribers.filter(id=request.user.id).exists()
        bad_request = None
        if request.method == "POST":
            if is_subscribed:
                bad_request = "You are already subscribed to this alert"
            else:
                alert.subscribers.add(request.user)
        else:
            if not is_subscribed:
                bad_request = "You are not subscribed to this alert"
            else:
                alert.subscribers.remove(request.user)
        if bad_request:
            return Response({"subscribe": bad_request}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(request=None, responses={200: AlertSerializer})
    @action(detail=True, methods=["POST", "DELETE"])
    def enable(self, request: Request, pk: str) -> Response:
        """Enable or disable an alert.

        POST: Enable the alert
        DELETE: Disable the alert

        Args:
            request (Request): The HTTP request object
            pk (str): Primary key of the alert

        Returns:
            Response: HTTP 200 with alert data on success, HTTP 400 with error on failure
        """
        alert = self.get_object()
        bad_request = None
        if request.method == "POST":
            if alert.enabled:
                bad_request = "This alert is already enabled"
            else:
                alert.enabled = True
        else:
            if not alert.enabled:
                bad_request = "This alert is already disabled"
            else:
                alert.enabled = False
        if bad_request:
            return Response({"enable": bad_request}, status=status.HTTP_400_BAD_REQUEST)
        alert.save(update_fields=["enabled"])
        return Response(self.get_serializer(instance=alert).data, status=status.HTTP_200_OK)
