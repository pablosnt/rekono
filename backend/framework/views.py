"""Base viewsets shared by all the Rekono API endpoints.

Implement the behaviour that every endpoint needs: restricting the objects to the
projects where the user is a member, assigning the owner of the created objects,
and the extra features of the likes and the statistics endpoints.
"""

from functools import cached_property
from typing import Any

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Exists, OuterRef, QuerySet
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
    """Base viewset that applies the project scoping and the ownership of Rekono.

    Attributes:
        ordering: Newest objects first, unless the endpoint orders them differently.
        http_method_names: Standard CRUD methods, with PATCH removed since partial
          updates aren't supported by the Rekono serializers.
        owner_field: Model field where the user that creates an object is saved, or
          None for the models that don't track their owner.
    """

    ordering = ["-id"]
    http_method_names = ["get", "post", "put", "delete"]
    owner_field = "owner"

    @cached_property
    def linked_model(self) -> type[BaseModel]:
        """The model managed by this viewset, taken from its serializer or filter."""
        for cls in [
            self.get_serializer_class(),
            self.filterset_class if hasattr(self, "filterset_class") else None,
        ]:
            if cls and hasattr(cls, "Meta") and hasattr(cls.Meta, "model"):
                return cls.Meta.model
        return BaseModel  # pragma: no cover

    def _get_project_from_data(self, project_field: str, data: dict[str, Any]) -> Project | None:
        """Get the project referenced by some validated data.

        Args:
            project_field: Path from the model to its project, using the Django
              double underscore notation, like "target__project".
            data: Validated data where the first field of the path is looked up.

        Returns:
            The referenced project, or None if the path can't be resolved because
            the data doesn't include it.
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
        """Get the objects from the projects where the user is a member.

        Models unrelated to a project are returned without this filter, since their
        access is only controlled by the permissions of the user.

        Returns:
            The objects that the user can access, or None for an unauthenticated
            request to a project-related model.
        """
        members_field = None
        if self.linked_model == Project:
            members_field = "members"
        elif self.linked_model._project_field:
            members_field = f"{self.linked_model._project_field}__members"
        if members_field:
            if self.request.user.id:
                return super().get_queryset().filter(**{members_field: self.request.user}).distinct()
            else:  # pragma: no cover
                return None
        return super().get_queryset().distinct()

    def get_serializer(self, *args: Any, **kwargs: Any) -> Serializer:
        """Get the serializer, adding the request to its context.

        The serializers need the request to know the user that performs it, so it's
        included here instead of relying on each caller to provide the context.

        Args:
            *args: Standard serializer arguments, like the instance or the data.
            **kwargs: Standard serializer arguments. A context given here is kept
              and only completed with the request.

        Returns:
            The serializer of this viewset, with the request in its context.
        """
        return self.get_serializer_class()(
            *args,
            **{
                **kwargs,
                "context": {**kwargs.get("context", {}), "request": self.request},
            },
        )

    def perform_create(self, serializer: Serializer) -> None:
        """Create the object, assigning the user that performs the request as owner.

        Args:
            serializer: Serializer with the validated data of the new object.

        Raises:
            PermissionDenied: If the new object belongs to a project where the user
              isn't a member. The permissions can't check this, since the project is
              only known after the data is validated.
        """
        project = self._get_project_from_data(self.linked_model._project_field, serializer.validated_data)
        if project and self.request.user not in project.members.all():
            raise PermissionDenied()
        if self.owner_field and self.linked_model and hasattr(self.linked_model, self.owner_field):
            serializer.save(**{self.owner_field: self.request.user})
            return
        super().perform_create(serializer)

    def _method_not_allowed(self, method: str) -> Response:
        """Build the response returned when an HTTP method isn't allowed.

        Args:
            method: HTTP method that was rejected, in any case.

        Returns:
            A 405 response reporting that method, in the same shape that DRF uses.
        """
        return Response(
            {"detail": f'Method "{method.upper()}" not allowed.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )


class LikeViewSet(BaseViewSet):
    """Base viewset for the models that can be liked by the users.

    Adds the like action and the annotations that the serializers and the filters
    need to expose the likes of each object.
    """

    def get_queryset(self) -> QuerySet:
        """Get the objects annotated with their number of likes and the user's like.

        The ``likes`` count is annotated with ``distinct=True`` and ``liked`` is
        resolved through an ``Exists`` subquery instead of a second join on the
        same many-to-many relation, so the two annotations don't inflate each
        other's row counts.

        Returns:
            The objects that the user can access, annotated with ``likes`` and
            ``liked``, which the serializers and the filters read.
        """
        return (
            super()
            .get_queryset()
            .annotate(
                likes=Count("liked_by", distinct=True),
                liked=Exists(
                    get_user_model().objects.filter(
                        pk=self.request.user.pk, **{f"liked_{self.queryset.model.__name__.lower()}": OuterRef("pk")}
                    )
                ),
            )
        )

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
        """Add the like of the user to this object with POST, or remove it with DELETE.

        Args:
            request: Request whose method decides whether the like is added or
              removed, and whose user is the one that likes the object.
            pk: Identifier of the object, taken from the URL.

        Returns:
            An empty 204 response, since the likes are read from the object itself.
        """
        if request.method == "POST":
            self.get_object().liked_by.add(request.user)
        else:
            self.get_object().liked_by.remove(request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class StatsViewSet(BaseViewSet):
    """Base viewset for the endpoints that return statistics.

    Attributes:
        ordering: No default ordering, since each statistic defines its own.
        http_method_names: GET only, because statistics are calculated, not stored.
        permission_classes: Only authentication is required, so any role can read
          the statistics of the projects where the user is a member.
    """

    ordering = []
    http_method_names = ["get"]
    permission_classes = [IsAuthenticated]


class LatestViewSet(StatsViewSet):
    """Base viewset for the endpoints that return a short ranking of items.

    The ranking itself is the ordering that each viewset declares, so it can be the
    most recent items or the ones that lead any other counter.

    Attributes:
        top_items: Number of items returned.
        pagination_class: None, since the number of items is already limited.
    """

    top_items = 5
    pagination_class = None

    def filter_queryset(self, queryset):
        """Filter the items as usual and keep only the first ones of the ordering.

        Args:
            queryset: Objects to be filtered.

        Returns:
            At most top_items objects, already ordered by the ranking criteria.
        """
        queryset = super().filter_queryset(queryset)
        return queryset[: self.top_items]
