"""Django REST framework views for Rekono's core framework.

Provides base ViewSet classes with integrated security controls, project-level
access control, and standardized CRUD operations for all Rekono API endpoints.
"""

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
    """Base ViewSet providing standardized REST API operations with security controls.

    Extends Django REST Framework's ModelViewSet with integrated logging,
    project-level access control, and ownership management. All API ViewSets
    in Rekono inherit from this base class to ensure consistent behavior.

    Security Features:
        - Project-level access control through membership validation
        - Automatic ownership assignment for created objects
        - Permission-based method restrictions
        - Integrated audit logging for all operations

    Attributes:
        ordering (list): Default ordering for query results.
        http_method_names (list): Allowed HTTP methods (excludes PATCH).
        owner_field (str): Field name for ownership assignment.
    """

    ordering = ["-id"]
    # Required to remove PATCH method
    http_method_names = ["get", "post", "put", "delete"]
    owner_field = "owner"

    @cached_property
    def linked_model(self) -> type[BaseModel]:
        """Get the model class associated with this ViewSet.

        Returns:
            type[BaseModel]: The model class from serializer or filterset metadata.
        """
        for cls in [
            self.get_serializer_class(),
            self.filterset_class if hasattr(self, "filterset_class") else None,
        ]:
            if cls and hasattr(cls, "Meta") and hasattr(cls.Meta, "model"):
                return cls.Meta.model
        return BaseModel

    def _get_project_from_data(self, project_field: str, data: dict[str, Any]) -> Project | None:
        """Extract project instance from nested data structure.

        Args:
            project_field (str): Field path to the project (e.g., "target__project").
            data (dict[str, Any]): The data dictionary to traverse.

        Returns:
            Project | None: The project instance or None if not found.
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
        """Get filtered queryset with project-level access control.

        Applies project membership filtering to ensure users only access
        resources from projects they belong to.

        Returns:
            QuerySet: Filtered queryset based on project membership.
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

        Args:
            *args (Any): Positional arguments for serializer.
            **kwargs (Any): Keyword arguments for serializer.

        Returns:
            Serializer: Configured serializer instance with request context.
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
        """Perform object creation with ownership and permission validation.

        Args:
            serializer (Serializer): The serializer instance for creation.

        Raises:
            PermissionDenied: If user is not a member of the associated project.
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
        """Generate method not allowed response.

        Args:
            method (str): The HTTP method that was attempted.

        Returns:
            Response: HTTP 405 Method Not Allowed response.
        """
        return Response(
            {"detail": f'Method "{method.upper()}" not allowed.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )


class LikeViewSet(BaseViewSet):
    """ViewSet for models with like/favorite functionality.

    Extends BaseViewSet with like management capabilities for user-interactive
    content such as tools, processes, and wordlists.

    Custom Actions:
        like: Add or remove likes from authenticated users

    Attributes:
        Inherits all BaseViewSet attributes with like count annotations.
    """

    def get_queryset(self) -> QuerySet:
        """Get queryset annotated with like counts.

        Returns:
            QuerySet: Base queryset with likes_count annotation.
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
        """Add or remove like from the current user.

        POST: Add like from current user
        DELETE: Remove like from current user

        Args:
            request (Request): The HTTP request object.
            pk (str): Primary key of the object to like/unlike.

        Returns:
            Response: HTTP 204 No Content on success.
        """
        if request.method == "POST":
            self.get_object_or_404().liked_by.add(request.user)
        else:
            self.get_object_or_404().liked_by.remove(request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)
