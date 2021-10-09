from projects.models import Project, Target, TargetPort
from projects.serializers import (AddProjectMemberSerializer,
                                  ProjectSerializer, TargetPortSerializer,
                                  TargetSerializer)
from rest_framework import status
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin, RetrieveModelMixin)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from users.models import User

# Create your views here.


class ProjectViewSet(ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class AddProjectMemberView(APIView):

    def post(self, request, pk):
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

    def delete(self, request, project_pk, member_pk):
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


class AddTargetPortView(APIView):

    def post(self, request, pk):
        try:
            target = Target.objects.get(pk=pk)
        except Target.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = TargetPortSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data.copy()
            data['target'] = target
            serializer.create(validated_data=data)
            return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteTargetPortView(APIView):

    def delete(self, request, target_pk, port_pk):
        try:
            target_port = TargetPort.objects.get(pk=port_pk, target__pk=target_pk)
            target_port.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except TargetPort.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
