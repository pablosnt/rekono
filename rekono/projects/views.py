from projects.models import Project, Target
from users.models import User
from projects.serializers import ProjectSerializer, TargetSerializer, AddProjectMemberSerializer
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin, RetrieveModelMixin)
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# Create your views here.


class ProjectViewSet(ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class AddProjectMemberView(APIView):

    def post(self, request, pk, format=None):
        try:
            project = Project.objects.get(pk=pk)
        except Project.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = AddProjectMemberSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.update(project, serializer.validated_data)
                return Response(status=status.HTTP_201_CREATED)
            except User.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
class DeleteProjectMemberView(APIView):

    def delete(self, request, project_pk, member_pk, format=None):
        try:
            project = Project.objects.get(pk=project_pk)
            member = User.objects.get(pk=member_pk, is_active=True)
        except (Project.DoesNotExist, User.DoesNotExist):
            return Response(status=status.HTTP_404_NOT_FOUND)
        if member in project.members.all() and member_pk != project.owner.id:
            project.members.remove(member)
            project.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class TargetViewSet(
    GenericViewSet,
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    DestroyModelMixin
):
    queryset = Target.objects.all()
    serializer_class = TargetSerializer
