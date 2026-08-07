"""Endpoints to create, cancel, and repeat the tasks."""

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
    """Create and list the tasks, and cancel or repeat the existing ones.

    Attributes:
        queryset: All the tasks, restricted to the projects of the user by the base
          viewset.
        serializer_class: Serializer of the tasks.
        filterset_class: Filters available to search tasks.
        permission_classes: Role permissions plus the membership in the project.
        search_fields: Fields used by the text search.
        ordering_fields: Fields that can be used to order the results.
        owner_field: Field that references the user that created each task.
        http_method_names: DELETE cancels a task instead of removing it, and the
          tasks can't be updated once they are created.
        tasks_queue: Queue where the tasks are enqueued and cancelled.
        executions_queue: Queue where the executions of a cancelled task are
          cancelled too.
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
        """Cancel a task, stopping the executions that didn't finish yet.

        The task itself is kept, so its history survives its cancellation. Running
        executions are stopped in their worker, while the ones that are still
        waiting are removed from the queue.

        Args:
            request: Request that asks for the task to be cancelled.
            pk: Identifier of the task, taken from the URL.
            *args: Standard view arguments.
            **kwargs: Standard view arguments.

        Returns:
            An empty response, or a validation error when all the executions of the
            task already finished, so there is nothing left to cancel.
        """
        task = self.get_object()
        has_executions = task.executions.exists()
        running_executions = task.executions.filter(status__in=Status.in_progress()).all()
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
                self.executions_queue.delete_job(execution.rq_job_id)
            self.logger.info(f"[Execution] Execution {execution.id} has been cancelled")
            execution.status = Status.CANCELLED
            execution.end = timezone.now()
            execution.save(update_fields=["status", "end"])
        task.end = timezone.now()
        task.save(update_fields=["end"])
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(request=None, responses={201: TaskSerializer})
    @action(detail=True, methods=["POST"])
    def repeat(self, request: Request, pk: str) -> Response:
        """Create and enqueue a new task with the same data as an existing one.

        The new task belongs to the user that repeats it, and it isn't scheduled or
        repeated even if the original one was.

        Args:
            request: Request whose user becomes the executor of the new task.
            pk: Identifier of the task to repeat, taken from the URL.

        Returns:
            The new task, or a validation error when the original one is still
            running or executes a configuration that has been deprecated.
        """
        task = self.get_object()
        if task.executions.filter(status__in=Status.in_progress()).exists():
            return Response({"task": "Task is still running"}, status=status.HTTP_400_BAD_REQUEST)
        if task.configuration and task.configuration.deprecated:  # pragma: no cover
            return Response(
                {"configuration": "Deprecated configurations can't be executed"}, status=status.HTTP_400_BAD_REQUEST
            )
        new_task = Task.objects.create(
            target=task.target,
            target_port=task.target_port,
            process=task.process,
            configuration=task.configuration,
            intensity=task.intensity,
            executor=request.user,
        )
        new_task.wordlists.set(task.wordlists.all())
        new_task.input_technologies.set(task.input_technologies.all())
        new_task.input_vulnerabilities.set(task.input_vulnerabilities.all())
        self.tasks_queue.enqueue(new_task)
        return Response(self.get_serializer(instance=new_task).data, status=status.HTTP_201_CREATED)


class LatestTasksViewSet(LatestViewSet):
    """Read the tasks that started most recently.

    Attributes:
        queryset: Tasks that already started, since the scheduled ones aren't
          activity yet.
        ordering: Most recent tasks first.
        serializer_class: Serializer of the tasks.
        filterset_class: Filters available to search tasks.
    """

    queryset = Task.objects.exclude(start=None)
    ordering = ["-start"]
    serializer_class = TaskSerializer
    filterset_class = TaskFilter
