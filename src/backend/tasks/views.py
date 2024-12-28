import logging
from typing import Any

import django_rq
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from executions.enums import Status
from executions.queues import ExecutionsQueue
from framework.views import BaseViewSet
from rekono.settings import CONFIG
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rq.command import send_stop_job_command
from security.authorization.permissions import (
    ProjectMemberPermission,
    RekonoModelPermission,
)
from tasks.filters import TaskFilter
from tasks.models import Task
from tasks.queues import TasksQueue
from tasks.serializers import TaskSerializer

# Create your views here.

logger = logging.getLogger()


class TaskViewSet(BaseViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    filterset_class = TaskFilter
    permission_classes = [
        IsAuthenticated,
        RekonoModelPermission,
        ProjectMemberPermission,
    ]
    search_fields = [
        "target__target",
        "process__name",
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
    http_method_names = ["get", "post", "delete"]
    tasks_queue = TasksQueue()
    executions_queue = ExecutionsQueue()

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
                self.tasks_queue.cancel_job(task.rq_job_id)
                self.tasks_queue.delete_job(task.rq_job_id)
                logger.info(f"[Task] Task {task.id} has been cancelled")
            connection = django_rq.get_connection("executions")
            for execution in running_executions:
                if not CONFIG.testing:  # pragma: no cover
                    if execution.status == Status.RUNNING:
                        send_stop_job_command(connection, execution.rq_job_id)
                    else:
                        self.executions_queue.cancel_job(execution.rq_job_id)
                logger.info(f"[Execution] Execution {execution.id} has been cancelled")
                execution.status = Status.CANCELLED
                execution.end = timezone.now()
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
    @action(detail=True, methods=["POST"])
    def repeat(self, request: Request, pk: str) -> Response:
        """Repeat task execution.

        Args:
            request (Request): Received HTTP request
            pk (str): Id of the task to repeat

        Returns:
            Response: HTTP response
        """
        task = self.get_object()
        if task.executions.filter(
            status__in=[Status.REQUESTED, Status.RUNNING]
        ).exists():
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
        new_task.input_technologies.set(task.input_technologies.all())
        new_task.input_vulnerabilities.set(task.input_vulnerabilities.all())
        self.tasks_queue.enqueue(new_task)
        return Response(
            TaskSerializer(instance=new_task).data, status=status.HTTP_201_CREATED
        )
