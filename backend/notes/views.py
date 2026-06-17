"""Django REST framework views for notes management.

Provides REST API endpoints for note CRUD operations, search capabilities,
and collaborative features including forking and like functionality.
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
    """ViewSet for managing notes with collaborative features.

    Provides REST API endpoints for note CRUD operations plus forking functionality
    for knowledge base development. Supports full-text search and filtering with
    project-level access control and ownership permissions.

    Custom Actions:
        fork: Create a copy of a public note owned by another user

    Attributes:
        queryset (QuerySet): All Note objects filtered by access permissions
        serializer_class (Serializer): Default serializer for note operations
        filterset_class (FilterSet): Filter class for querying notes
        permission_classes (list): Required permissions for access
        search_fields (list): Fields that can be searched
        ordering_fields (list): Fields that can be used for ordering
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
            "likes_count",
        ]
    )

    def _get_project_from_data(self, project_field: str, data: dict[str, Any]) -> Project | None:
        """Extract project context from entity associations in request data.

        Iterates through all possible entity relationships to determine the project
        context for a note based on the associated entity.

        Args:
            project_field (str): The project field name (unused but required by interface)
            data (dict[str, Any]): Request data containing entity associations

        Returns:
            Project | None: The project associated with the entity, or None if no association
        """
        for link in links:
            if data.get(link):
                return cast(BaseModel, data.get(link)).parent_project

    def get_queryset(self) -> QuerySet:
        """Filter queryset to show only accessible notes.

        Returns notes that are either owned by the current user or are public
        and within projects where the user is a member.

        Returns:
            QuerySet: Filtered queryset of accessible notes
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

        Allows users to fork public notes created by other users, creating a private
        copy with all content, relationships, and tags preserved. Forked notes
        maintain a reference to the original note.

        Args:
            request (Request): The HTTP request object
            pk (str): Primary key of the note to fork

        Returns:
            Response: Serialized forked note data or 404 if not allowed

        Note:
            Only public notes owned by other users can be forked. Forked notes
            are always created as public and belong to the requesting user.
        """
        note = self.get_object()
        # Only allow forking of public notes that the user doesn't own once
        if (
            note.public
            and note.owner.id != self.request.user.id
            and not note.forks.filter(owner=self.request.user).exists()
        ):
            # Create a new note with all the same content and relationships
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
                public=False,  # Forked notes are always private
                forked_from=note,  # Reference to the original note
            )
            # Copy all tags from the original note
            fork.tags.set(note.tags.all())
            return Response(self.get_serializer(instance=fork).data, status=HTTP_201_CREATED)
        return Response(status=HTTP_404_NOT_FOUND)
