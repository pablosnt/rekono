from defectdojo import uploader
from defectdojo.exceptions import (EngagementIdNotFoundException,
                                   InvalidEngagementIdException,
                                   ProductIdNotFoundException)
from defectdojo.serializers import EngagementSerializer
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import PermissionDenied
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin, RetrieveModelMixin)
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from targets.models import Target
from tasks import services
from tasks.exceptions import InvalidTaskException
from tasks.filters import TaskFilter
from tasks.models import Task
from tasks.queue import producer
from tasks.serializers import TaskSerializer

# Create your views here.


class TaskViewSet(
    GenericViewSet,
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    DestroyModelMixin
):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    filterset_class = TaskFilter

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

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            services.cancel_task(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except InvalidTaskException:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(request=EngagementSerializer, responses={200: None})
    @action(
        detail=True,
        methods=['POST'],
        url_path='defect-dojo-scans',
        url_name='defect-dojo-scans'
    )
    def defect_dojo(self, request, pk):
        task = self.get_object()
        serializer = EngagementSerializer(data=request.data)
        if serializer.is_valid():
            try:
                uploader.upload_executions(
                    task.executions.all(),
                    serializer.validated_data.get('engagement_id'),
                    serializer.validated_data.get('engagement_name'),
                    serializer.validated_data.get('engagement_description')
                )
                return Response(status=status.HTTP_200_OK)
            except (
                ProductIdNotFoundException,
                EngagementIdNotFoundException,
                InvalidEngagementIdException
            ) as ex:
                return Response(str(ex), status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(request=None, responses={200: None})
    @action(detail=True, methods=['POST'], url_path='repeat', url_name='repeat')
    def execute_again(self, request, pk):
        task = self.get_object()
        producer(task, task.parameters.all(), get_current_site(request).domain)
        return Response(status=status.HTTP_200_OK)
