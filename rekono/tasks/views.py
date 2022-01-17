from defectdojo.views import DefectDojoFindings, DefectDojoScans
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import PermissionDenied, ValidationError
from drf_spectacular.utils import extend_schema
from findings.models import (OSINT, Credential, Endpoint, Enumeration, Exploit,
                             Host, Technology, Vulnerability)
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin, RetrieveModelMixin)
from rest_framework.response import Response
from targets.models import Target
from tasks import services
from tasks.enums import Status
from tasks.filters import TaskFilter
from tasks.models import Task
from tasks.queue import producer
from tasks.serializers import TaskSerializer

# Create your views here.


class TaskViewSet(
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    DestroyModelMixin,
    DefectDojoScans,
    DefectDojoFindings
):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    filterset_class = TaskFilter
    search_fields = ['target__target', 'process__name', 'process__steps__tool__name', 'tool__name']

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(target__project__members=self.request.user)

    def perform_create(self, serializer):
        project_check = Target.objects.filter(
            id=serializer.validated_data.get('target').id,
            project__members=self.request.user
        ).exists()
        if not project_check:
            raise PermissionDenied()
        serializer.save(executor=self.request.user)

    def get_executions(self):
        return list(self.get_object().executions.all())

    def get_findings(self):
        task = self.get_object()
        findings = []
        for find_model in [
            OSINT, Host, Enumeration, Technology,
            Endpoint, Vulnerability, Credential, Exploit
        ]:
            findings.extend(find_model.objects.filter(
                execution__task=task,
                is_active=True
            ).all())
        return findings

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            services.cancel_task(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValidationError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(request=None, responses={200: TaskSerializer})
    @action(detail=True, methods=['POST'], url_path='repeat', url_name='repeat')
    def repeat_task(self, request, pk):
        task = self.get_object()
        if task.status in [Status.REQUESTED, Status.RUNNING]:
            return Response('Execution is still running', status=status.HTTP_400_BAD_REQUEST)
        new_task = Task.objects.create(
            target=task.target,
            process=task.process,
            tool=task.tool,
            configuration=task.configuration,
            intensity=task.intensity,
            executor=request.user
        )
        new_task.wordlists.set(task.wordlists.all())
        new_task.save()
        producer(new_task)
        serializer = TaskSerializer(instance=new_task)
        return Response(serializer.data, status=status.HTTP_200_OK)
