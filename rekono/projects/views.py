from django.core.exceptions import PermissionDenied
from drf_spectacular.utils import extend_schema
from integrations.defect_dojo import executions as dd_uploader
from integrations.defect_dojo.exceptions import (EngagementIdNotFoundException,
                                                 ProductIdNotFoundException)
from projects.models import Project, Target
from projects.serializers import (ProjectMemberSerializer, ProjectSerializer,
                                  TargetPortSerializer, TargetSerializer)
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin, RetrieveModelMixin)
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from executions.models import Execution
from users.models import User
from users.serializers import UserSerializer

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

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(members=self.request.user).order_by('-id')

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
            dd_uploader.upload(executions)
            return Response(status=status.HTTP_200_OK)
        except (ProductIdNotFoundException, EngagementIdNotFoundException) as ex:
            return Response(str(ex), status=status.HTTP_400_BAD_REQUEST)


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

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(project__members=self.request.user).order_by('-id')

    def perform_create(self, serializer):
        project_check = bool(
            self.request.user in serializer.validated_data.get('project').members.all()
        )
        if not project_check:
            raise PermissionDenied()
        super().perform_create(serializer)

    @extend_schema(responses={200: TargetPortSerializer})
    @action(detail=True, methods=['GET'], url_path='ports', url_name='ports')
    def target_ports(self, request, pk):
        target = self.get_object()
        serializer = TargetPortSerializer(target.target_ports.all(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(request=TargetPortSerializer, responses={201: TargetPortSerializer})
    @target_ports.mapping.post
    def add_target_port(self, request, pk):
        target = self.get_object()
        serializer = TargetPortSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data.copy()
            data['target'] = target
            serializer.create(validated_data=data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=['DELETE'],
        url_path='ports/(?P<port_id>[0-9])',
        url_name='delete_port'
    )
    def delete_target_port(self, request, port_id, pk):
        target = self.get_object()
        target_port = get_object_or_404(target.target_ports, pk=port_id)
        target_port.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
