from typing import Any, Optional, cast

from django.db.models import Q, QuerySet
from drf_spectacular.utils import extend_schema
from framework.models import BaseModel
from framework.views import LikeViewSet
from notes.filters import NoteFilter
from notes.models import Note
from notes.serializers import NoteSerializer, links
from projects.models import Project
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_404_NOT_FOUND
from security.authorization.permissions import (
    OwnerPermission,
    ProjectMemberPermission,
    RekonoModelPermission,
)


class NoteViewSet(LikeViewSet):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    filterset_class = NoteFilter
    permission_classes = [
        IsAuthenticated,
        RekonoModelPermission,
        ProjectMemberPermission,
        OwnerPermission,
    ]
    search_fields = ["title", "body"]
    ordering_fields = (
        [
            "id",
        ]
        + links
        + [
            "title",
            "tags",
            "owner",
            "created_at",
            "updated_at",
            "likes_count",
        ]
    )
    http_method_names = ["get", "post", "put", "delete"]

    def _get_project_from_data(
        self, project_field: str, data: dict[str, Any]
    ) -> Optional[Project]:
        data_links = [link for link in reversed(links) if data.get(link)]
        return (
            cast(BaseModel, data.get(data_links[0])).get_project()
            if len(data_links) > 0
            else None
        )

    def get_queryset(self) -> QuerySet:
        return (
            super()
            .get_queryset()
            .filter(
                Q(owner=self.request.user)
                | (
                    Q(public=True)
                    & (
                        Q(project__members=self.request.user)
                        | Q(target__project__members=self.request.user)
                        | (Q(project=None) & Q(target=None))
                    )
                )
            )
        )

    @extend_schema(request=None, responses={201: NoteSerializer})
    @action(
        detail=True,
        methods=["POST"],
        permission_classes=[
            IsAuthenticated,
            RekonoModelPermission,
            ProjectMemberPermission,
        ],
    )
    def fork(self, request: Request, pk: str) -> Response:
        note = self.get_object()
        if note.public and note.owner.id != self.request.user.id:
            fork = Note.objects.create(
                project=note.project,
                target=note.target,
                title=note.title,
                body=note.body,
                owner=self.request.user,
                public=False,
                forked_from=note,
            )
            fork.tags.set(note.tags.all())
            return Response(
                self.get_serializer(instance=fork).data, status=HTTP_201_CREATED
            )
        return Response(status=HTTP_404_NOT_FOUND)
