"""Endpoints to manage the projects and their members."""

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
    """Manage the projects and the users that are members of them.

    Attributes:
        queryset: All the projects, restricted to the ones of the user by the base
          viewset.
        serializer_class: Serializer of the projects.
        filterset_class: Filters available to search projects.
        permission_classes: Role permissions plus the membership in the project.
        search_fields: Fields used by the text search, including the targets, so a
          project can be found by what it scans.
        ordering_fields: Fields that can be used to order the results.
    """

    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    filterset_class = ProjectFilter
    permission_classes = [IsAuthenticated, RekonoModelPermission, ProjectMemberPermission]
    search_fields = ["name", "description", "targets__target"]
    ordering_fields = ["id", "name", "owner"]

    @action(detail=True, methods=["POST", "DELETE"], url_path="members/(?P<member_id>[0-9]+)")
    def members(self, request: Request, member_id: str, pk: str) -> Response:
        """Add a member to the project with POST, or remove them with DELETE.

        The alert subscriptions follow the membership, so a new member is subscribed
        to the alerts that subscribe all the members, and a removed one stops
        receiving all the alerts of the project.

        Args:
            request: Request whose method decides whether the member is added or
              removed.
            member_id: Identifier of the user, taken from the URL.
            pk: Identifier of the project, taken from the URL.

        Returns:
            An empty response, or a validation error when the member to remove is
            the owner of the project, who can never be removed.

        Raises:
            Http404: If the user doesn't exist or isn't a member of the project.
        """
        project = self.get_object()
        if request.method == "POST":
            member = get_object_or_404(User.objects.all(), pk=member_id, is_active=True)
            project.members.add(member)
            for alert in project.alerts.filter(subscribe_all_members=True, enabled=True).all():
                alert.subscribers.add(member)
        else:
            member = get_object_or_404(project.members, pk=member_id)
            if member.id == project.owner.id:
                return Response({"user": ["The project owner can't be removed"]}, status=status.HTTP_400_BAD_REQUEST)
            project.members.remove(member)
            for alert in project.alerts.filter(subscribers=member).all():
                alert.subscribers.remove(member)
        return Response(status=status.HTTP_204_NO_CONTENT)


class TopProjectsViewSet(LatestViewSet):
    """Read the projects with the most security activity.

    Attributes:
        queryset: Projects annotated with the counters that rank them.
        ordering: Vulnerabilities first, and the rest of the counters as tiebreakers.
        serializer_class: Serializer of the projects.
        filterset_class: Filters available to search projects.
    """

    queryset = (
        Project.objects.annotate(targets_count=Count("targets", distinct=True))
        .annotate(tasks_count=Count("targets__tasks", distinct=True))
        .annotate(
            hosts_count=Count(
                "targets__tasks__executions__host",
                distinct=True,
                # Fixed hosts are excluded so remediated findings don't inflate the activity ranking
                filter=Q(targets__tasks__executions__host__is_fixed=False),
            )
        )
        .annotate(
            vulnerabilities_count=Count(
                "targets__tasks__executions__vulnerability",
                distinct=True,
                # Only vulnerabilities confirmed by a scan execution count towards the ranking:
                # false positives, fixed vulnerabilities, and user-reported findings are excluded
                filter=~Q(targets__tasks__executions__vulnerability__triage_status=TriageStatus.FALSE_POSITIVE)
                & Q(targets__tasks__executions__vulnerability__is_fixed=False)
                & Q(targets__tasks__executions__vulnerability__created_from_user_input=False),
            )
        )
    )
    ordering = ["-vulnerabilities_count", "-hosts_count", "-tasks_count", "-targets_count"]
    serializer_class = ProjectSerializer
    filterset_class = ProjectFilter
