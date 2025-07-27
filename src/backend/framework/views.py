"""This module contains common view logic and API endpoints."""

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
    """Base viewset that provides common functionality for all API viewsets.

    This abstract base class extends Django REST Framework's ModelViewSet and
    LoggingEntity to provide project-based authorization, automatic owner
    assignment, and logging capabilities.

    Attributes:
        ordering (list): Default ordering for queryset results.
        http_method_names (list): Allowed HTTP methods (excludes PATCH).
        owner_field (str): Field name for automatic owner assignment.
    """

    ordering = ["-id"]
    # Required to remove PATCH method
    http_method_names = ["get", "post", "put", "delete"]
    owner_field = "owner"

    @cached_property
    def linked_model(self) -> type[BaseModel]:
        """Get the model class linked to this viewset.

        Determines the model by examining the serializer class or filterset class.
        Falls back to BaseModel if no model can be determined.

        Returns:
            The model class associated with this viewset.
        """
        for cls in [
            self.get_serializer_class(),
            self.filterset_class if hasattr(self, "filterset_class") else None,
        ]:
            if cls and hasattr(cls, "Meta") and hasattr(cls.Meta, "model"):
                return cls.Meta.model
        return BaseModel

    def _get_project_from_data(self, project_field: str, data: dict[str, Any]) -> Project | None:
        """Extract project from request data using field path.

        Traverses the project field path in the data to find the associated
        project instance.

        Args:
            project_field: double-underscore-separated field path to the project.
            data: Request data dictionary.

        Returns:
            The project instance if found, None otherwise.
        """
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
        """Get the filtered queryset based on project membership.

        Filters the queryset to only include objects that belong to projects
        where the current user is a member. If the model is not project-linked,
        returns the full queryset.

        Returns:
            Filtered queryset based on user's project membership.
        """
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

    def get_serializer(self, *args: Any, **kwargs: Any) -> Serializer:
        """Get serializer instance with request context.

        Ensures the original request is passed to the serializer context
        for use in serializer methods.

        Args:
            *args: Positional arguments for serializer.
            **kwargs: Keyword arguments for serializer.

        Returns:
            Serializer instance with request context.
        """
        return self.get_serializer_class()(
            *args,
            **{
                **kwargs,
                # Pass original request to serializers
                "context": {**kwargs.get("context", {}), "request": self.request},
            },
        )

    def perform_create(self, serializer: Serializer) -> None:
        """Perform object creation with authorization checks.

        Checks project membership before creating related entities and
        automatically assigns the current user as owner if configured.

        Args:
            serializer: The serializer instance with validated data.

        Raises:
            PermissionDenied: If user is not a member of the project.
        """
        project = self._get_project_from_data(self.linked_model._project_field, serializer.validated_data)
        # Check project membership before creating related entities
        if project and self.request.user not in project.members.all():
            raise PermissionDenied()
        if self.owner_field and self.linked_model and hasattr(self.linked_model, self.owner_field):
            serializer.save(**{self.owner_field: self.request.user})
            return
        super().perform_create(serializer)

    def _method_not_allowed(self, method: str) -> Response:
        """Return a standardized method not allowed response.

        Args:
            method: The HTTP method that was not allowed.

        Returns:
            HTTP 405 response with error details.
        """
        return Response(
            {"detail": f'Method "{method.upper()}" not allowed.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )


class LikeViewSet(BaseViewSet):
    """Viewset for likeable entities with like/unlike functionality.

    Extends BaseViewSet to provide like/unlike actions for entities that
    support user likes. Includes automatic like count annotation.
    """

    def get_queryset(self) -> QuerySet:
        """Get queryset with like count annotation.

        Returns:
            Queryset annotated with the count of users who liked each entity.
        """
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
        """Like or unlike an entity.

        POST request adds the current user to the entity's liked_by list.
        DELETE request removes the current user from the entity's liked_by list.

        Args:
            request: The HTTP request object.
            pk: Primary key of the entity to like/unlike.

        Returns:
            HTTP 204 No Content response on success.
        """
        if request.method == "POST":
            self.get_object().liked_by.add(request.user)
        else:
            self.get_object().liked_by.remove(request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)
