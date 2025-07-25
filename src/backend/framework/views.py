from functools import cached_property
from typing import Any

from django.core.exceptions import PermissionDenied
from django.db.models import Count, QuerySet
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.viewsets import ModelViewSet

from framework.logging import LoggingEntity
from framework.models import BaseModel
from projects.models import Project
from security.authorization.permissions import IsAuditor


class BaseViewSet(ModelViewSet, LoggingEntity):
    ordering = ["-id"]
    # Required to remove PATCH method
    http_method_names = ["get", "post", "put", "delete"]
    owner_field = "owner"

    @cached_property
    def linked_model(self) -> type[BaseModel]:
        for cls in [
            self.get_serializer_class(),
            self.filterset_class if hasattr(self, "filterset_class") else None,
        ]:
            if cls and hasattr(cls, "Meta") and hasattr(cls.Meta, "model"):
                return cls.Meta.model
        return BaseModel

    def _get_project_from_data(self, project_field: str, data: dict[str, Any]) -> Project | None:
        fields = project_field.split("__")
        if not fields:
            return None
        data = data.get(fields[0], {})
        for field in fields[1:]:
            if hasattr(data, field):
                data = getattr(data, field)
            else:  # pragma: no cover
                return None
        return data if isinstance(data, Project) else None

    def get_queryset(self) -> QuerySet:
        members_field = None
        if self.linked_model == Project:
            members_field = "members"
        elif self.linked_model._project_field:
            members_field = f"{self.linked_model._project_field}__members"
        if members_field:
            if self.request.user.id:
                # Read authorization based on project membership
                return super().get_queryset().filter(**{members_field: self.request.user}).distinct()
            else:  # pragma: no cover
                return None
        return super().get_queryset().distinct()

    def get_serializer(self, *args, **kwargs):
        return self.get_serializer_class()(
            *args,
            **{
                **kwargs,
                # Pass original request to serializers
                "context": {**kwargs.get("context", {}), "request": self.request},
            },
        )

    def perform_create(self, serializer: Serializer) -> None:
        project = self._get_project_from_data(self.linked_model._project_field, serializer.validated_data)
        # Check project membership before creating related entities
        if project and self.request.user not in project.members.all():
            raise PermissionDenied()
        if self.owner_field and self.linked_model and hasattr(self.linked_model, self.owner_field):
            serializer.save(**{self.owner_field: self.request.user})
            return
        super().perform_create(serializer)

    def _method_not_allowed(self, method: str) -> Response:
        return Response(
            {"detail": f'Method "{method.upper()}" not allowed.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )


class LikeViewSet(BaseViewSet):
    def get_queryset(self) -> QuerySet:
        return super().get_queryset().annotate(likes_count=Count("liked_by"))

    @extend_schema(request=None, responses={204: None})
    # Permission classes are overwritten to IsAuthenticated and IsAuditor, because only Tools, Processes and Wordlists
    # can be liked. Administrators and auditors can read these resources, but not all the auditors can make POST
    # requests, according to the default permissions.
    @action(
        detail=True,
        methods=["POST", "DELETE"],
        permission_classes=[IsAuthenticated, IsAuditor],
    )
    def like(self, request: Request, pk: str) -> Response:
        if request.method == "POST":
            self.get_object().liked_by.add(request.user)
        else:
            self.get_object().liked_by.remove(request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)
