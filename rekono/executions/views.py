from executions.exceptions import InvalidTaskException
from rest_framework.views import APIView
from executions.models import Execution, Task
from executions.serializers import ExecutionSerializer, TaskSerializer
from rest_framework import status
from rest_framework.mixins import (CreateModelMixin, ListModelMixin,
                                   RetrieveModelMixin, DestroyModelMixin)
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from executions import services

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

    def perform_create(self, serializer):
        serializer.save(executor=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            services.cancel_task(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except InvalidTaskException:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        

class ExecutionViewSet(
    GenericViewSet,
    ListModelMixin,
    RetrieveModelMixin
):
    queryset = Execution.objects.all()
    serializer_class = ExecutionSerializer
    filterset_fields = {
        'task': ['exact'],
        'task__target': ['exact'],
        'task__target__project': ['exact'],
        'task__process': ['exact'],
        'task__tool': ['exact'],
        'task__intensity': ['exact'],
        'task__executor': ['exact'],
        'status': ['exact'],
        'step__tool': ['exact'],
        'start': ['gte', 'lte', 'exact'],
        'end': ['gte', 'lte', 'exact']
    }
