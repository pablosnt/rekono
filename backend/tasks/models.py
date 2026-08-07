"""Model of the tasks that request a target to be scanned."""

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from framework.models import BaseModel
from parameters.models import InputTechnology, InputVulnerability
from processes.models import Process
from rekono.settings import AUTH_USER_MODEL
from security.validators.input_validator import FutureDatetimeValidator
from target_ports.models import TargetPort
from targets.models import Target
from tasks.enums import TimeUnit
from tools.enums import Intensity
from tools.models import Configuration
from wordlists.models import Wordlist


class Task(BaseModel):
    """Request to scan a target, either with one tool configuration or with a process.

    Attributes:
        rq_job_id: Identifier of the job in the tasks queue, needed to cancel it
          while it's still scheduled.
        target: Target to be scanned.
        process: Process to be executed, or None when the task executes one single
          configuration.
        configuration: Tool configuration to be executed, or None when the task
          executes a process.
        intensity: How aggressive the executions of the task are.
        executor: User that created the task.
        scheduled_at: Moment when the task will be executed, or None to execute it
          right away.
        repeat_in: Number of time units to wait before executing the task again.
        repeat_time_unit: Unit of the interval between repetitions.
        creation: Moment when the task was created.
        enqueued_at: Moment when the task was enqueued.
        start: Moment when the first execution of the task started.
        end: Moment when the last execution of the task finished.
        target_port: Port that the scan is limited to, or None to scan all the
          ports of the target.
        wordlists: Wordlists that the executions of the task will use.
        input_technologies: Technologies that the auditor provides to the executions.
        input_vulnerabilities: Vulnerabilities that the auditor provides to the
          executions.
    """

    rq_job_id = models.TextField(max_length=50, blank=True, null=True)
    target = models.ForeignKey(Target, related_name="tasks", on_delete=models.CASCADE)
    process = models.ForeignKey(Process, related_name="tasks", blank=True, null=True, on_delete=models.SET_NULL)
    configuration = models.ForeignKey(
        Configuration, related_name="tasks", on_delete=models.SET_NULL, blank=True, null=True
    )
    intensity = models.IntegerField(choices=Intensity.choices, default=Intensity.NORMAL)
    executor = models.ForeignKey(
        AUTH_USER_MODEL, related_name="tasks", on_delete=models.SET_NULL, blank=True, null=True
    )
    scheduled_at = models.DateTimeField(
        blank=True,
        null=True,
        validators=[FutureDatetimeValidator(code="scheduled_at")],
    )
    repeat_in = models.IntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1), MaxValueValidator(60)],
    )
    repeat_time_unit = models.TextField(max_length=10, choices=TimeUnit.choices, blank=True, null=True)
    creation = models.DateTimeField(auto_now_add=True)
    enqueued_at = models.DateTimeField(blank=True, null=True)
    start = models.DateTimeField(blank=True, null=True)
    end = models.DateTimeField(blank=True, null=True)
    target_port = models.ForeignKey(TargetPort, related_name="tasks", on_delete=models.SET_NULL, blank=True, null=True)
    wordlists = models.ManyToManyField(Wordlist, related_name="tasks", blank=True)
    input_technologies = models.ManyToManyField(InputTechnology, related_name="tasks", blank=True)
    input_vulnerabilities = models.ManyToManyField(InputVulnerability, related_name="tasks", blank=True)

    _project_field = "target__project"

    def __str__(self) -> str:
        """Return the target and the process or configuration to be executed."""
        return f"{self.target.__str__()} - {(self.process or self.configuration).__str__()}"

    def get_scoped_target_ports(self) -> list[TargetPort]:
        """Get the target ports that define the scope of this task.

        A task-specific target port restricts scanning to that single port so a
        scan does not spread to the whole target. When no task target port is set,
        all of the target's ports are used. Findings discovered by previous
        executions still take priority at runtime, since Port findings and
        TargetPorts share the same Port input type and seeded target ports are
        skipped once findings of that type exist.

        Returns:
            The target port of the task when it has one, and all the ports of the
            target otherwise, which is empty when the target has none.
        """
        return [self.target_port] if self.target_port else list(self.target.target_ports.all())

    @staticmethod
    def get_target(target: Target, target_port: TargetPort | None = None) -> str:
        """Build the label that identifies what a task scans.

        Args:
            target: Target being scanned.
            target_port: Port that the scan is limited to, if there is one.

        Returns:
            The target with the port and path when the scan is limited to one port,
            and the bare target otherwise, so notifications and Telegram prompts
            show the exact scope in a single line.
        """
        return (
            f"{target.target}:{target_port.port}{target.clean_path(target_port.path) if target_port.path else ''}"
            if target_port
            else target.target
        )
