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
    filterset_fields = {
        'name': ['exact', 'contains'],
        'description': ['exact', 'contains'],
        'owner': ['exact'],
        'members': ['exact'],
    }
    ordering_fields = ('name', 'owner')
    http_method_names = ['get', 'post', 'put', 'delete']

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class AddProjectMemberView(APIView):
    serializer_class = AddProjectMemberSerializer

    def post(self, request, pk):
        try:
            project = Project.objects.get(pk=pk)
        except Project.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            try:
                serializer.update(project, serializer.validated_data)
                return Response(status=status.HTTP_201_CREATED)
            except User.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
class DeleteProjectMemberView(APIView):
    serializer_class = None

    def delete(self, request, pk, member_id):
        try:
            project = Project.objects.get(pk=pk)
            member = User.objects.get(pk=member_id, is_active=True)
        except (Project.DoesNotExist, User.DoesNotExist):
            return Response(status=status.HTTP_404_NOT_FOUND)
        if member in project.members.all() and member_id != project.owner.id:
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
    filterset_fields = {
        'project__name': ['exact', 'contains'],
        'project__description': ['exact', 'contains'],
        'project__owner': ['exact'],
        'target': ['exact', 'contains'],
        'type': ['exact'],
    }
    ordering_fields = ('project', 'target', 'type')


class AddTargetPortView(APIView):
    serializer_class = TargetPortSerializer

    def post(self, request, pk):
        try:
            target = Target.objects.get(pk=pk)
        except Target.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data.copy()
            data['target'] = target
            serializer.create(validated_data=data)
            return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteTargetPortView(APIView):
    serializer_class = None

    def delete(self, request, pk, port_id):
        try:
            target_port = TargetPort.objects.get(pk=port_id, target__pk=pk)
            target_port.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except TargetPort.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
