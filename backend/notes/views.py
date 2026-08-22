"""Viewsets of the note endpoints."""

from typing import Any, cast

from django.db.models import Q, QuerySet
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_404_NOT_FOUND

from framework.models import BaseModel
from framework.views import LikeViewSet
from notes.filters import NoteFilter
from notes.models import Note
from notes.serializers import NoteSerializer, links
from projects.models import Project
from security.authorization.permissions import (
    OwnerPermission,
    ProjectMemberPermission,
    RekonoModelPermission,
)


class NoteViewSet(LikeViewSet):
    """Manage the notes of a project and the copies made from them.

    Attributes:
        queryset: All the notes, filtered later by ownership and visibility.
        serializer_class: Serializer of the notes.
        filterset_class: Filters of the notes.
        permission_classes: Role permissions plus the membership in the project and
          the ownership of the note, so only its owner can update or remove it.
        search_fields: Free text search over the title and the content of the note.
        ordering_fields: Fields that the notes can be sorted by, including all the
          things that a note can be about.
    """

    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    filterset_class = NoteFilter
    permission_classes = [IsAuthenticated, RekonoModelPermission, ProjectMemberPermission, OwnerPermission]
    search_fields = ["title", "body"]
    ordering_fields = (
        [
            "id",
        ]
        + links
        + [
            "title",
            "owner",
            "created_at",
            "updated_at",
            "liked",
            "likes",
        ]
    )

    def _get_project_from_data(self, project_field: str, data: dict[str, Any]) -> Project | None:
        """Get the project of the thing that the new note is about.

        Args:
            project_field: Not used, since the project of a note comes from the
              thing that it's about instead of from a field of the request.
            data: Data of the note that is being created.

        Returns:
            The project that the note will belong to, or None if the note isn't
            about anything yet.
        """
        for link in links:
            if data.get(link):
                return cast(BaseModel, data.get(link)).parent_project

    def get_queryset(self) -> QuerySet:
        """Get the notes of the user, plus the public ones of their projects.

        Returns:
            The notes that the user can read, so a private note never leaves its
            owner.
        """
        return (
            super()
            .get_queryset()
            .filter(Q(owner=self.request.user) | (Q(public=True) & Q(project__members=self.request.user)))
        )

    # By default, only admin and auditors are able to like entities, since readers have no write access to
    # Tools, Processes or Wordlists, the other models that use LikeViewSet
    # Notes are different: readers already have full add, change and delete access on their own notes, so
    # the role restriction is dropped here and any project member can like a note
    @extend_schema(request=None, responses={204: None})
    @action(
        detail=True,
        methods=["POST", "DELETE"],
        permission_classes=[IsAuthenticated, ProjectMemberPermission],
    )
    def like(self, request: Request, pk: str) -> Response:
        """Like a note with POST, or remove the like with DELETE.

        Args:
            request: Request whose method decides whether the like is added or
              removed, and whose user is the one that likes the note.
            pk: Identifier of the note, taken from the URL.

        Returns:
            An empty 204 response.
        """
        return super().like(request, pk)

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
        """Create a private copy of a public note written by another user.

        Args:
            request: Request whose user becomes the owner of the copy.
            pk: Identifier of the note to fork, taken from the URL.

        Returns:
            The created copy, with the same content, links, and tags as the
            original note, or a not found error if the note can't be forked
            because it isn't public, because it belongs to the user that makes
            the request, or because they already have a copy of it.
        """
        note = self.get_object()
        if (
            note.public
            and note.owner.id != self.request.user.id
            and not note.forks.filter(owner=self.request.user).exists()
        ):
            fork = Note.objects.create(
                project=note.project,
                target=note.target,
                task=note.task,
                osint=note.osint,
                host=note.host,
                port=note.port,
                path=note.path,
                credential=note.credential,
                technology=note.technology,
                vulnerability=note.vulnerability,
                exploit=note.exploit,
                title=note.title,
                body=note.body,
                owner=self.request.user,
                public=False,
                forked_from=note,
            )
            fork.tags.set(note.tags.all())
            return Response(self.get_serializer(instance=fork).data, status=HTTP_201_CREATED)
        return Response(status=HTTP_404_NOT_FOUND)
