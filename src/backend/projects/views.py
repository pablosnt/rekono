from drf_spectacular.utils import extend_schema
from framework.views import BaseViewSet
from projects.filters import ProjectFilter
from projects.models import Project
from projects.serializers import ProjectMemberSerializer, ProjectSerializer
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from security.authorization.permissions import (
    ProjectMemberPermission,
    RekonoModelPermission,
)

# Create your views here.


class ProjectViewSet(BaseViewSet):
    """Project ViewSet that includes: get, retrieve, create, update, delete and Defect-Dojo features."""

    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    filterset_class = ProjectFilter
    permission_classes = [
        IsAuthenticated,
        RekonoModelPermission,
        ProjectMemberPermission,
    ]
    search_fields = ["name", "description"]  # Fields used to search projects
    ordering_fields = ["id", "name"]

    @extend_schema(request=ProjectMemberSerializer, responses={201: None})
    @action(detail=True, methods=["POST"], url_path="members", url_name="members")
    def add_member(self, request: Request, pk: str) -> Response:
        """Add user to the project members.

        Args:
            request (Request): Received HTTP request
            pk (str): Instance Id

        Returns:
            Response: HTTP Response
        """
        project = self.get_object()
        serializer = ProjectMemberSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.update(project, serializer.validated_data)
        return Response(status=status.HTTP_201_CREATED)

    @action(
        detail=True,
        methods=["DELETE"],
        url_path="members/(?P<member_id>[0-9])",
        url_name="remove_member",
    )
    def remove_member(self, request: Request, member_id: str, pk: str) -> Response:
        """Remove user from the project members.

        Args:
            request (Request): Received HTTP request
            member_id (str): User Id to be removed
            pk (str): Instance Id

        Returns:
            Response: HTTP Response
        """
        project = self.get_object()
        member = get_object_or_404(project.members, pk=member_id)
        if int(member_id) != project.owner.id:
            # Member found and it isn't the project owner
            project.members.remove(member)  # Remove project member
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {"user": ["The project owner can't be removed"]},
            status=status.HTTP_400_BAD_REQUEST,
        )
