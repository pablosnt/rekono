from defectdojo import uploader
from defectdojo.exceptions import (EngagementIdNotFoundException,
                                   ProductIdNotFoundException)
from drf_spectacular.utils import extend_schema
from executions.models import Execution
from projects.filters import ProjectFilter
from projects.models import Project
from projects.serializers import ProjectMemberSerializer, ProjectSerializer
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from users.models import User
from users.serializers import UserSerializer

# Create your views here.


class ProjectViewSet(ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    filterset_class = ProjectFilter
    http_method_names = ['get', 'post', 'put', 'delete']

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(members=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @extend_schema(responses={200: UserSerializer})
    @action(detail=True, methods=['GET'], url_path='members', url_name='members')
    def project_members(self, request, pk):
        project = self.get_object()
        serializer = UserSerializer(project.members.all(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(request=ProjectMemberSerializer, responses={201: ProjectMemberSerializer})
    @project_members.mapping.post
    def add_project_member(self, request, pk):
        project = self.get_object()
        serializer = ProjectMemberSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.update(project, serializer.validated_data)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except User.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=['DELETE'],
        url_path='members/(?P<member_id>[0-9])',
        url_name='delete_member'
    )
    def delete_project_member(self, request, member_id, pk):
        project = self.get_object()
        member = get_object_or_404(project.members, pk=member_id)
        if member in project.members.all() and member_id != project.owner.id:
            project.members.remove(member)
            project.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(request=None, responses={200: None})
    @action(detail=True, methods=['POST'], url_path='defect-dojo', url_name='defect-dojo')
    def defect_dojo(self, request, pk):
        project = self.get_object()
        try:
            executions = Execution.objects.filter(task__target__project=project).all()
            uploader.upload_executions(executions)
            return Response(status=status.HTTP_200_OK)
        except (ProductIdNotFoundException, EngagementIdNotFoundException) as ex:
            return Response(str(ex), status=status.HTTP_400_BAD_REQUEST)
