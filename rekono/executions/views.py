from executions.exceptions import InvalidTaskException
from rest_framework.views import APIView
from executions.models import Execution, Task
from executions.serializers import ExecutionSerializer, TaskSerializer
from rest_framework import status
from rest_framework.mixins import (CreateModelMixin, ListModelMixin,
                                   RetrieveModelMixin)
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from executions import services

# Create your views here.


class TaskViewSet(
    GenericViewSet,
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin
):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def perform_create(self, serializer):
        serializer.save(executor=self.request.user)


class ExecutionViewSet(
    GenericViewSet,
    ListModelMixin,
    RetrieveModelMixin
):
    queryset = Execution.objects.all()
    serializer_class = ExecutionSerializer


class CancelTaskView(APIView):

    def post(self, request, pk, format=None):
        try:
            req = Task.objects.get(pk=pk)
        except Task.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        try:
            services.cancel_task(req)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except InvalidTaskException:
            return Response(status=status.HTTP_400_BAD_REQUEST)
