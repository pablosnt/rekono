from django.core.exceptions import PermissionDenied
from drf_spectacular.utils import extend_schema
from defectdojo import uploader
from defectdojo.exceptions import (EngagementIdNotFoundException,
                                                 ProductIdNotFoundException)
from projects.models import Target
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin, RetrieveModelMixin)
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from tasks import services
from tasks.exceptions import InvalidTaskException
from tasks.models import Task
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
    filterset_fields = {
        'target': ['exact'],
        'target__project': ['exact'],
        'process': ['exact'],
        'tool': ['exact'],
        'intensity': ['exact'],
        'executor': ['exact'],
        'status': ['exact'],
        'start': ['gte', 'lte', 'exact'],
        'end': ['gte', 'lte', 'exact']
    }
    ordering_fields = (
        'target', 'target__project', 'process', 'tool', 'intensity', 'executor',
        'status', 'start', 'end'
    )

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(target__project__members=self.request.user).order_by('-id')

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

    @extend_schema(request=None, responses={200: None})
    @action(detail=True, methods=['POST'], url_path='defect-dojo', url_name='defect-dojo')
    def defect_dojo(self, request, pk):
        task = self.get_object()
        try:
            uploader.upload_executions(task.executions.all())
            return Response(status=status.HTTP_200_OK)
        except (ProductIdNotFoundException, EngagementIdNotFoundException) as ex:
            return Response(str(ex), status=status.HTTP_400_BAD_REQUEST)
