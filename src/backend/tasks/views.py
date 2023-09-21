import logging
from typing import Any

import django_rq
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from executions.enums import Status
from framework.views import BaseViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rq.command import send_stop_job_command
from tasks.filters import TaskFilter
from tasks.models import Task
from tasks.serializers import TaskSerializer

# Create your views here.

logger = logging.getLogger()


class TaskViewSet(BaseViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    filterset_class = TaskFilter
    search_fields = [
        "target__target",
        "process__name",
        "process__steps__configuration__tool__name",
        "configuration__name",
        "configuration__tool__name",
    ]
    ordering_fields = [
        "id",
        "target",
        "process",
        "configuration",
        "configuration__tool",
        "creation",
        "enqueued_at",
        "start",
        "end",
    ]
    owner_field = "executor"
    http_method_names = [
        "get",
        "post",
        "delete",
    ]

    def destroy(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Cancel task.

        Args:
            request (Request): Received HTTP request

        Returns:
            Response: HTTP response
        """
        task = self.get_object()
        running_executions = task.executions.filter(
            status__in=[Status.REQUESTED, Status.RUNNING]
        ).all()
        if running_executions:
            if task.rq_job_id:
                # TODO: cancel queue job
                logger.info(f"[Task] Task {task.id} has been cancelled")
            connection = django_rq.get_connection("executions-queue")
            for execution in running_executions:
                if execution.status == Status.RUNNING:
                    send_stop_job_command(connection, execution.rq_job_id)
                else:
                    # TODO: cancel queue job
                    pass
                logger.info(f"[Execution] Execution {execution.id} has been cancelled")
                execution.status = Status.CANCELLED  # Set execution status to Cancelled
                execution.end = timezone.now()  # Update execution end date
                execution.save(update_fields=["status", "end"])
            task.end = timezone.now()
            task.save(update_fields=["end"])
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            logger.warning(f"[Task] Task {task.id} can't be cancelled")
            return Response(
                {"task": f"Task {task.id} can't be cancelled"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @extend_schema(request=None, responses={200: TaskSerializer})
    @action(detail=True, methods=["POST"], url_path="repeat", url_name="repeat")
    def repeat_task(self, request: Request, pk: str) -> Response:
        """Repeat task execution.

        Args:
            request (Request): Received HTTP request
            pk (str): Id of the task to repeat

        Returns:
            Response: HTTP response
        """
        task = self.get_object()
        if task.is_running():
            return Response(
                {"task": "Task is still running"}, status=status.HTTP_400_BAD_REQUEST
            )
        new_task = Task.objects.create(
            target=task.target,
            process=task.process,
            configuration=task.configuration,
            intensity=task.intensity,
            executor=request.user,
        )
        new_task.wordlists.set(task.wordlists.all())  # Add wordlists from original task
        # TODO: Enqueue new task
        return Response(
            TaskSerializer(instance=new_task).data, status=status.HTTP_201_CREATED
        )
