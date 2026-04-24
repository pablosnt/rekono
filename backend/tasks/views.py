"""Django REST framework views for task management.

Provides REST API views for task records with CRUD operations, task cancellation,
repetition functionality, and proper authentication and authorization controls.
"""

from typing import Any

import django_rq
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rq.command import send_stop_job_command
from rq.exceptions import NoSuchJobError

from executions.enums import Status
from executions.queues import ExecutionsQueue
from framework.views import BaseViewSet, LatestViewSet
from rekono.settings import CONFIG
from security.authorization.permissions import ProjectMemberPermission, RekonoModelPermission
from tasks.filters import TaskFilter
from tasks.models import Task
from tasks.queues import TasksQueue
from tasks.serializers import TaskSerializer


class TaskViewSet(BaseViewSet):
    """ViewSet for Task model CRUD operations and task management.

    Provides REST API endpoints for managing security testing tasks with filtering,
    searching, ordering capabilities. Includes advanced features for task
    cancellation and repetition with proper execution cleanup.

    Custom Actions:
        repeat: Create a duplicate task for re-execution

    Attributes:
        queryset (QuerySet): Task model instances
        serializer_class (Serializer): Serializer for Task model
        filterset_class (FilterSet): Filter class for query filtering
        permission_classes (list): Required permissions for access control
        search_fields (list): Fields available for text search
        ordering_fields (list): Fields available for result ordering
        owner_field (str): Field used for ownership-based permissions
        http_method_names (list): Allowed HTTP methods (GET, POST, DELETE)
        tasks_queue (TasksQueue): Queue manager for task operations
        executions_queue (ExecutionsQueue): Queue manager for execution operations
    """

    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    filterset_class = TaskFilter
    permission_classes = [IsAuthenticated, RekonoModelPermission, ProjectMemberPermission]
    search_fields = ["target__target", "process__name", "configuration__name", "configuration__tool__name"]
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

    def destroy(self, request: Request, pk: str, *args: Any, **kwargs: Any) -> Response:
        """Cancel and delete a task with proper cleanup of running executions.

        Handles task cancellation by stopping queued jobs, cancelling running
        executions, and performing proper cleanup. Tasks with completed
        executions cannot be cancelled.

        Args:
            request (Request): The HTTP request object
            pk (str): Primary key of the task
            *args (Any): Additional positional arguments
            **kwargs (Any): Additional keyword arguments

        Returns:
            Response: HTTP 204 on successful cancellation, HTTP 400 if task cannot be cancelled
        """
        task = self.get_object()
        has_executions = task.executions.exists()
        running_executions = task.executions.filter(status__in=[Status.REQUESTED, Status.RUNNING]).all()
        if not running_executions.exists() and has_executions:
            self.logger.warning(f"[Task] Task {task.id} can't be cancelled")
            return Response({"task": f"Task {task.id} can't be cancelled"}, status=status.HTTP_400_BAD_REQUEST)
        if task.rq_job_id:  # pragma: no cover
            self.tasks_queue.cancel_job(task.rq_job_id)
            self.tasks_queue.delete_job(task.rq_job_id)
            self.logger.info(f"[Task] Task {task.id} has been cancelled")
        connection = django_rq.get_connection("executions")
        for execution in running_executions:
            if not CONFIG.testing:  # pragma: no cover
                if execution.status == Status.RUNNING:
                    try:
                        send_stop_job_command(connection, execution.rq_job_id)
                    except NoSuchJobError:
                        pass
                else:
                    self.executions_queue.cancel_job(execution.rq_job_id)
                # TOTEST:
                self.executions_queue.delete_job(execution.rq_job_id)
            self.logger.info(f"[Execution] Execution {execution.id} has been cancelled")
            execution.status = Status.CANCELLED
            execution.end = timezone.now()
            execution.save(update_fields=["status", "end"])
        task.end = timezone.now()
        task.save(update_fields=["end"])
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(request=None, responses={200: TaskSerializer})
    @action(detail=True, methods=["POST"])
    def repeat(self, request: Request, pk: str) -> Response:
        """Create a duplicate task for re-execution.

        Creates a new task with the same configuration as the original task,
        including all associated wordlists, technologies, and vulnerabilities.
        The new task is immediately enqueued for execution.

        Args:
            request (Request): The HTTP request object
            pk (str): Primary key of the task to repeat

        Returns:
            Response: HTTP 201 with new task data on success, HTTP 400 if task is still running
        """
        task = self.get_object()
        if task.executions.filter(status__in=[Status.REQUESTED, Status.RUNNING]).exists():
            return Response({"task": "Task is still running"}, status=status.HTTP_400_BAD_REQUEST)
        if task.configuration and task.configuration.deprecated:  # pragma: no cover
            return Response(
                {"configuration": "Deprecated configurations can't be executed"}, status=status.HTTP_400_BAD_REQUEST
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
        return Response(self.get_serializer(instance=new_task).data, status=status.HTTP_201_CREATED)


class LatestTasksViewSet(LatestViewSet):
    """ViewSet for retrieving latest task execution statistics.

    Provides the most recently started tasks, excluding those without
    a start time. Ordered by start time in descending order.

    Attributes:
        queryset: Tasks with non-null start times
        ordering: Most recent tasks first
        serializer_class: Task serialization
        filterset_class: Task filtering capabilities
    """

    queryset = Task.objects.exclude(start=None)
    ordering = ["-start"]
    serializer_class = TaskSerializer
    filterset_class = TaskFilter
