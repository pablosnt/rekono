"""Django REST framework views for project management.

Provides REST API views for project CRUD operations with team member management,
access control enforcement, and automated alert subscription handling.
"""

from django.db.models import Count, Q
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from findings.enums import TriageStatus
from framework.views import BaseViewSet, LatestViewSet
from projects.filters import ProjectFilter
from projects.models import Project
from projects.serializers import ProjectSerializer
from security.authorization.permissions import (
    ProjectMemberPermission,
    RekonoModelPermission,
)
from users.models import User


class ProjectViewSet(BaseViewSet):
    """ViewSet for Project model operations with team member management.

    Provides REST API endpoints for project CRUD operations plus custom actions
    for team member management with automated alert subscription handling.

    Custom Actions:
        members: Add/remove team members with automated alert subscription management

    Attributes:
        queryset (QuerySet): Project model instances
        serializer_class (Serializer): Serializer for Project model
        filterset_class (FilterSet): Filter class for query filtering
        permission_classes (list): Required permissions for access control
        search_fields (list): Fields available for text search
        ordering_fields (list): Fields available for result ordering
    """

    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    filterset_class = ProjectFilter
    permission_classes = [IsAuthenticated, RekonoModelPermission, ProjectMemberPermission]
    search_fields = ["name", "description", "targets__target"]
    ordering_fields = ["id", "name"]

    @action(detail=True, methods=["POST", "DELETE"], url_path="members/(?P<member_id>[0-9])")
    def members(self, request: Request, member_id: str, pk: str) -> Response:
        """Manage project team member membership with automated alert subscriptions.

        Handles adding and removing team members from projects with automatic
        management of alert subscriptions based on project alert configurations.

        POST: Add user to project members and subscribe to relevant alerts
        DELETE: Remove user from project members and unsubscribe from all project alerts

        Args:
            request (Request): The HTTP request object
            member_id (str): User ID of the member to add/remove
            pk (str): Primary key of the project

        Returns:
            Response: HTTP 204 on success, HTTP 400 if trying to remove project owner

        Raises:
            Http404: If user or project member not found
        """
        project = self.get_object()
        if request.method == "POST":
            member = get_object_or_404(User.objects.all(), pk=member_id, is_active=True)
            project.members.add(member)
            # Subscribe the new member to the default alerts
            for alert in project.alerts.filter(subscribe_all_members=True, enabled=True).all():
                alert.subscribers.add(member)
        else:
            member = get_object_or_404(project.members, pk=member_id)
            if member.id == project.owner.id:
                return Response({"user": ["The project owner can't be removed"]}, status=status.HTTP_400_BAD_REQUEST)
            project.members.remove(member)
            # Unsubscribe the new member from the project alerts
            for alert in project.alerts.filter(subscribers=member).all():
                alert.subscribers.remove(member)
        return Response(status=status.HTTP_204_NO_CONTENT)


class TopProjectsViewSet(LatestViewSet):
    """ViewSet for retrieving top project statistics by activity.

    Provides projects ranked by security findings and activity metrics,
    annotated with counts of targets, tasks, hosts, and vulnerabilities.

    Attributes:
        queryset: Projects with comprehensive activity annotations
        ordering: Prioritizes projects with most vulnerabilities and activity
        serializer_class: Project serialization
        filterset_class: Project filtering capabilities
    """

    queryset = (
        Project.objects.annotate(targets_count=Count("targets", distinct=True))
        .annotate(tasks_count=Count("targets__tasks", distinct=True))
        .annotate(
            hosts_count=Count(
                "targets__tasks__executions__host",
                distinct=True,
                filter=Q(targets__tasks__executions__host__is_fixed=False),
            )
        )
        .annotate(
            vulnerabilities_count=Count(
                "targets__tasks__executions__vulnerability",
                distinct=True,
                filter=~Q(targets__tasks__executions__vulnerability__triage_status=TriageStatus.FALSE_POSITIVE)
                & Q(targets__tasks__executions__vulnerability__is_fixed=False)
                & Q(targets__tasks__executions__vulnerability__created_from_user_input=False),
            )
        )
    )
    ordering = ["-vulnerabilities_count", "-hosts_count", "-tasks_count", "-targets_count"]
    serializer_class = ProjectSerializer
    filterset_class = ProjectFilter
