"""Viewsets of the alert endpoints."""

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
    """Manage the alerts of a project and the subscriptions to them.

    Attributes:
        queryset: All the alerts, filtered later by project membership.
        serializer_class: Serializer of the alerts.
        filterset_class: Filters of the alerts.
        permission_classes: Role permissions plus the membership in the project and
          the ownership of the alert, so only its owner can update or remove it.
        search_fields: Free text search over the item and the value of the alert.
        ordering_fields: Fields that the alerts can be sorted by.
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
        """Get the serializer that only allows the value change for the updates.

        Returns:
            The edit serializer for PUT, which only exposes the value, and the
            standard one for the rest of the methods.
        """
        return EditAlertSerializer if self.request.method == "PUT" else super().get_serializer_class()

    def get_queryset(self) -> QuerySet:
        """Get the alerts, keeping only the ones that can be updated for the updates.

        Returns:
            All the alerts, or only the enabled ones whose item is filtered by a
            value, since the value is the only thing that an update can change.
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
        """Subscribe to an alert with POST, or unsubscribe from it with DELETE.

        Args:
            request: Request whose method decides whether the user subscribes or
              unsubscribes.
            pk: Identifier of the alert, taken from the URL.

        Returns:
            An empty response, or a validation error when the user is already
            subscribed to the alert or isn't subscribed to it yet.
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
        """Enable an alert with POST, or disable it with DELETE.

        Args:
            request: Request whose method decides the new state of the alert.
            pk: Identifier of the alert, taken from the URL.

        Returns:
            The updated alert, or a validation error when the alert is already in
            the requested state.
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
