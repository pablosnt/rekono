"""Task models for Rekono.

Defines the Task model for managing security testing task execution with scheduling,
dependency management, and execution coordination. Supports both single tool
execution and complex multi-step security processes.
"""

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
    """Model representing security testing tasks for tool and process execution.

    Represents a security testing task that can execute either a single security tool
    or a complete multi-step security process against a target. Supports advanced
    scheduling, recurring execution, and comprehensive parameter management.

    Attributes:
        rq_job_id (TextField): Redis Queue job identifier for background processing (optional, max 50 characters)
        target (ForeignKey): Target system for task execution
        process (ForeignKey): Multi-step process to execute (optional, mutually exclusive with configuration)
        configuration (ForeignKey): Single tool configuration to execute (optional, mutually exclusive with process)
        intensity (IntegerField): Execution intensity level from Intensity enum (default: NORMAL)
        executor (ForeignKey): User who created and owns this task (optional)
        scheduled_at (DateTimeField): Future execution time for scheduled tasks (optional)
        repeat_in (IntegerField): Interval value for recurring tasks (1-60, optional)
        repeat_time_unit (TextField): Time unit for repeat interval from TimeUnit enum (optional)
        creation (DateTimeField): Task creation timestamp (auto-generated)
        enqueued_at (DateTimeField): When task was queued for execution (optional)
        start (DateTimeField): Task execution start time (optional)
        end (DateTimeField): Task execution completion time (optional)
        target_port (ForeignKey): Specific target port for task execution (optional)
        wordlists (ManyToManyField): Wordlists to use during execution
        input_technologies (ManyToManyField): Technology inputs for tool execution
        input_vulnerabilities (ManyToManyField): Vulnerability inputs for tool execution

    Example:
        Create a scheduled tool task:

        ```python
        task = Task.objects.create(
            target=my_target,
            configuration=nmap_config,
            intensity=Intensity.HIGH,
            executor=user,
            scheduled_at=datetime.now() + timedelta(hours=1),
            repeat_in=24,
            repeat_time_unit=TimeUnit.HOURS
        )
        ```
    """

    # Job Id in the tasks queue
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
    # Date when the task will be executed
    scheduled_at = models.DateTimeField(
        blank=True,
        null=True,
        validators=[FutureDatetimeValidator(code="scheduled_at")],
    )
    # Amount of time to wait until repeating the task execution
    repeat_in = models.IntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1), MaxValueValidator(60)],
    )
    # Time unit to apply to the 'repeat in' value
    repeat_time_unit = models.TextField(max_length=10, choices=TimeUnit.choices, blank=True, null=True)
    creation = models.DateTimeField(auto_now_add=True)
    # Date at task got enqueued
    enqueued_at = models.DateTimeField(blank=True, null=True)
    start = models.DateTimeField(blank=True, null=True)
    end = models.DateTimeField(blank=True, null=True)
    target_port = models.ForeignKey(TargetPort, related_name="tasks", on_delete=models.SET_NULL, blank=True, null=True)
    wordlists = models.ManyToManyField(Wordlist, related_name="tasks", blank=True)
    input_technologies = models.ManyToManyField(InputTechnology, related_name="tasks", blank=True)
    input_vulnerabilities = models.ManyToManyField(InputVulnerability, related_name="tasks", blank=True)

    _project_field = "target__project"

    def __str__(self) -> str:
        """Return string representation of the task.

        Returns:
            str: String in format "target - process/configuration"
        """
        return f"{self.target.__str__()} - {(self.process or self.configuration).__str__()}"

    def get_scoped_target_ports(self) -> list[TargetPort]:
        """Return the target ports that define this task's scan scope.

        A task-specific target port restricts scanning to that single port so a
        scan does not spread to the whole target. When no task target port is set,
        all of the target's ports are used. Findings discovered by previous
        executions still take priority at runtime, since Port findings and
        TargetPorts share the same Port input type and seeded target ports are
        skipped once findings of that type exist.

        Returns:
            list[TargetPort]: The single task target port when set, otherwise all
                              of the target's ports (empty when it has none).
        """
        return [self.target_port] if self.target_port else list(self.target.target_ports.all())


    @staticmethod
    def get_target(target: Target, target_port: TargetPort | None = None) -> str:
        """Build a display label for a target, optionally scoped to a target port.

        Combines the target with a specific port and path when a target port is
        given, so notifications and Telegram prompts can show the exact scan
        scope in a single line. When no target port is provided, the bare target
        is returned to indicate that all of the target's ports are in scope.

        Args:
            target (Target): The target being scanned.
            target_port (TargetPort | None): The target port scoping the scan, if any.

        Returns:
            str: "<target>:<port><path>" when a target port is given, otherwise
                 the bare target address.
        """
        return f"{target.target}:{target_port.port}{target.clean_path(target_port.path) if target_port.path else ""}" if target_port else target.target