from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from framework.views import BaseViewSet
from projects.filters import ProjectFilter
from projects.models import Project
from projects.serializers import ProjectSerializer
from security.authorization.permissions import (
    ProjectMemberPermission,
    RekonoModelPermission,
)
from users.models import User


class ProjectViewSet(BaseViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    filterset_class = ProjectFilter
    permission_classes = [
        IsAuthenticated,
        RekonoModelPermission,
        ProjectMemberPermission,
    ]
    search_fields = ["name", "description"]
    ordering_fields = ["id", "name"]

    @action(detail=True, methods=["POST", "DELETE"], url_path="members/(?P<member_id>[0-9])")
    def members(self, request: Request, member_id: str, pk: str) -> Response:
        project = self.get_object()
        if request.method == "POST":
            member = get_object_or_404(User, pk=member_id)
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
