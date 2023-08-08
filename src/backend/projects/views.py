from framework.views import BaseViewSet
from projects.filters import ProjectFilter
from projects.models import Project
from projects.serializers import ProjectSerializer

# Create your views here.


# GetViewSet, CreateWithUserViewSet
class ProjectViewSet(BaseViewSet):
    """Project ViewSet that includes: get, retrieve, create, update, delete and Defect-Dojo features."""

    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    filterset_class = ProjectFilter
    search_fields = ["name", "description"]  # Fields used to search projects
    ordering_fields = ["id", "name"]

    # members_field = "members"
    # user_field = "owner"

    # @extend_schema(request=ProjectMemberSerializer, responses={201: None})
    # @action(detail=True, methods=["POST"], url_path="members", url_name="members")
    # def add_project_member(self, request: Request, pk: str) -> Response:
    #     """Add user to the project members.

    #     Args:
    #         request (Request): Received HTTP request
    #         pk (str): Instance Id

    #     Returns:
    #         Response: HTTP Response
    #     """
    #     project = self.get_object()
    #     serializer = ProjectMemberSerializer(data=request.data)
    #     if serializer.is_valid():
    #         try:
    #             serializer.update(
    #                 project, serializer.validated_data
    #             )  # Add project member
    #             return Response(status=status.HTTP_201_CREATED)
    #         except User.DoesNotExist:
    #             return Response(status=status.HTTP_404_NOT_FOUND)  # User not found
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # @action(
    #     detail=True,
    #     methods=["DELETE"],
    #     url_path="members/(?P<member_id>[0-9])",
    #     url_name="delete_member",
    # )
    # def delete_project_member(
    #     self, request: Request, member_id: str, pk: str
    # ) -> Response:
    #     """Remove user from the project members.

    #     Args:
    #         request (Request): Received HTTP request
    #         member_id (str): User Id to be removed
    #         pk (str): Instance Id

    #     Returns:
    #         Response: HTTP Response
    #     """
    #     project = self.get_object()
    #     member = get_object_or_404(
    #         project.members, pk=member_id
    #     )  # Get member from project members
    #     if int(member_id) != project.owner.id:
    #         # Member found and it isn't the project owner
    #         project.members.remove(member)  # Remove project member
    #         return Response(status=status.HTTP_204_NO_CONTENT)
    #     return Response(status=status.HTTP_400_BAD_REQUEST)
