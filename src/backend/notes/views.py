from typing import Any, Dict, Optional, cast

from django.db.models import Q, QuerySet
from drf_spectacular.utils import extend_schema
from framework.views import LikeViewSet
from notes.filters import NoteFilter
from notes.models import Note
from notes.serializers import NoteSerializer
from projects.models import Project
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED
from security.authorization.permissions import (
    OwnerPermission,
    ProjectMemberPermission,
    RekonoModelPermission,
)
from targets.models import Target

# Create your views here.


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
    ordering_fields = [
        "id",
        "project",
        "target",
        "title",
        "tags",
        "owner",
        "created_at",
        "updated_at",
    ]
    http_method_names = ["get", "post", "put", "delete"]

    def _get_project_from_data(
        self, project_field: str, data: Dict[str, Any]
    ) -> Optional[Project]:
        return data.get("project") or (
            cast(Target, data.get("target")).project if data.get("target") else None
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
    @action(detail=True, methods=["POST"], url_path="fork", url_name="fork")
    def target(self, request: Request, pk: str) -> Response:
        note = self.get_object()
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
        return Response(NoteSerializer(fork).data, status=HTTP_201_CREATED)
