from typing import Any, Dict, Optional

from django.core.exceptions import PermissionDenied
from django.db.models import Count, QuerySet
from drf_spectacular.utils import extend_schema
from framework.models import BaseModel
from projects.models import Project
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.viewsets import ModelViewSet
from security.authorization.permissions import IsAuditor


class BaseViewSet(ModelViewSet):
    ordering = ["-id"]
    # Required to remove PATCH method
    http_method_names = ["get", "post", "put", "delete"]
    owner_field = "owner"

    def _get_model(self) -> BaseModel:
        for cls in [
            self.get_serializer_class(),
            self.filterset_class if hasattr(self, "filterset_class") else None,
        ]:
            if cls and hasattr(cls, "Meta") and hasattr(cls.Meta, "model"):
                return cls.Meta.model

    def _get_project_from_data(
        self, project_field: str, data: Dict[str, Any]
    ) -> Optional[Project]:
        fields = project_field.split("__")
        if not fields:
            return None
        data = data.get(fields[0], {})
        for field in fields[1:]:
            if hasattr(data, field):
                data = getattr(data, field)
            else:  # pragma: no cover
                return None
        return data

    def get_queryset(self) -> QuerySet:
        model = self._get_model()
        members_field = None
        if model:
            if model == Project:
                members_field = "members"
            else:
                project_field = model.get_project_field()
                if project_field:
                    members_field = f"{project_field}__members"
        if members_field:
            if self.request.user.id:
                project_filter = {members_field: self.request.user}
                return super().get_queryset().filter(**project_filter)
            else:  # pragma: no cover
                return None
        return super().get_queryset()

    def perform_create(self, serializer: Serializer) -> None:
        model = self._get_model()
        if model:
            project = self._get_project_from_data(
                model.get_project_field() or "", serializer.validated_data
            )
            if project and self.request.user not in project.members.all():
                raise PermissionDenied()
        if self.owner_field and model and hasattr(model, self.owner_field):
            parameters = {self.owner_field: self.request.user}
            serializer.save(**parameters)
            return
        super().perform_create(serializer)

    def _method_not_allowed(self, method: str) -> Response:
        return Response(
            {"detail": f'Method "{method.upper()}" not allowed.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )


class LikeViewSet(BaseViewSet):
    """Base ViewSet that includes the like and dislike features."""

    def get_queryset(self) -> QuerySet:
        """Get the model queryset. It's required for allow the access to the likes count by the child ViewSets.

        Returns:
            QuerySet: Model queryset
        """
        return super().get_queryset().annotate(likes_count=Count("liked_by"))

    @extend_schema(request=None, responses={204: None})
    # Permission classes are overrided to IsAuthenticated and IsAuditor, because currently only Tools, Processes and
    # Wordlists can be liked, and auditors and admins are the only ones that can see this resources.
    # Permission classes should be overrided here, because if not, the standard permissions would be applied, and not
    # all auditors can make POST requests to resources like these.
    @action(
        detail=True,
        methods=["POST", "DELETE"],
        permission_classes=[IsAuthenticated, IsAuditor],
    )
    def like(self, request: Request, pk: str) -> Response:
        """Mark an instance as liked by the current user.

        Args:
            request (Request): Received HTTP request
            pk (str): Instance Id

        Returns:
            Response: HTTP Response
        """
        if request.method == "POST":
            self.get_object().liked_by.add(request.user)
        else:
            self.get_object().liked_by.remove(request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)
