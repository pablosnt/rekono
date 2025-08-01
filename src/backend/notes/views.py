"""Views for the notes app.

This module provides Django REST Framework views for the Note model,
enabling API endpoints for note management, forking functionality, and
complex filtering based on user permissions and note visibility.
"""

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
    """ViewSet for managing Note model instances with forking capabilities.

    This ViewSet provides API endpoints for listing, retrieving, creating,
    updating, and deleting Note instances. It includes a custom fork action
    that allows users to create copies of public notes.

    The ViewSet implements complex filtering logic to show users only the
    notes they have access to:
    - Notes owned by the current user
    - Public notes from projects where the user is a member

    It also supports advanced filtering, searching, and ordering capabilities
    while enforcing proper authentication and authorization.

    Attributes:
        queryset: All Note instances (filtered by get_queryset).
        serializer_class: NoteSerializer for data conversion.
        filterset_class: NoteFilter for query filtering.
        permission_classes: Authentication and authorization requirements.
        search_fields: Fields that can be searched via the API.
        ordering_fields: Fields that can be used for result ordering.
        http_method_names: Allowed HTTP methods (GET, POST, PUT, DELETE).
    """

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

    def _get_project_from_data(self, project_field: str, data: dict[str, Any]) -> Project | None:
        """Extract project from note data by checking entity relationships.

        This helper method determines the project context for a note by
        examining the entity relationships in the provided data. It iterates
        through all possible entity links to find the first one that has
        a value, then extracts the project from that entity.

        Args:
            project_field: The project field name (unused, kept for compatibility).
            data: Dictionary containing note data with entity relationships.

        Returns:
            The Project instance if found, None otherwise.
        """
        for link in links:
            if data.get(link):
                return cast(BaseModel, data.get(link)).parent_project
        return None

    def get_queryset(self) -> QuerySet:
        """Get filtered queryset based on user permissions and note visibility.

        This method implements complex filtering logic to ensure users only
        see notes they have access to:

        1. Notes owned by the current user (regardless of public/private status)
        2. Public notes from projects where the user is a member

        This ensures proper data isolation and privacy while allowing
        collaboration on public notes within project teams.

        Returns:
            Filtered QuerySet containing only accessible notes.
        """
        return (
            super()
            .get_queryset()
            .filter(Q(owner=self.request.user) | (Q(public=True) & Q(project__members=self.request.user)))
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
        """Create a fork (copy) of a public note.

        This action allows users to create a personal copy of a public note.
        The forked note inherits all the content and tags from the original
        but becomes private and owned by the forking user.

        Forking is only allowed for:
        1. Public notes (private notes cannot be forked)
        2. Notes not owned by the current user (users cannot fork their own notes)

        The forked note maintains a reference to the original note through
        the forked_from field, enabling tracking of note lineage.

        Args:
            request: The HTTP request object.
            pk: The primary key of the note to fork.

        Returns:
            HTTP 201 with the serialized forked note on success.
            HTTP 404 if forking is not allowed.
        """
        note = self.get_object_or_404()

        # Only allow forking of public notes that the user doesn't own
        if note.public and note.owner.id != self.request.user.id:
            # Create a new note with all the same content and relationships
            fork = Note.objects.create(
                project=note.project,
                target=note.target,
                task=note.task,
                execution=note.execution,
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
                public=False,  # Forked notes are always private
                forked_from=note,  # Reference to the original note
            )

            # Copy all tags from the original note
            fork.tags.set(note.tags.all())

            return Response(self.get_serializer(instance=fork).data, status=HTTP_201_CREATED)

        return Response(status=HTTP_404_NOT_FOUND)
