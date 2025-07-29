"""Django models for alert management and monitoring.

This module contains the database models for the alerts system, including
the main Alert model for configuration and MonitorSettings for automated
monitoring jobs.
"""

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from alerts.enums import AlertItem, AlertMode
from executions.models import Execution
from findings.enums import PortStatus, TriageStatus
from findings.models import (
    OSINT,
    Credential,
    Finding,
    Host,
    Port,
    Technology,
    Vulnerability,
)
from framework.models import BaseModel
from projects.models import Project
from rekono.settings import AUTH_USER_MODEL
from security.validators.input_validator import Regex, Validator


class Alert(BaseModel):
    """Model for configuring and managing alerts.

    This model represents an alert configuration that can trigger notifications
    based on different types of findings and conditions. Alerts can be configured
    for various item types (OSINT, hosts, ports, etc.) and different modes
    (new findings, filtered findings, monitoring).

    Attributes:
        project: The project this alert belongs to
        item: The type of finding this alert monitors
        mode: How the alert should trigger (new, filter, monitor)
        value: Optional filter value for specific criteria
        enabled: Whether this alert is currently active
        subscribe_all_members: Whether to auto-subscribe all project members
        owner: The user who created this alert
        subscribers: Users subscribed to receive notifications for this alert
    """

    project = models.ForeignKey(Project, related_name="alerts", on_delete=models.CASCADE)
    item = models.TextField(max_length=15, choices=AlertItem.choices)
    mode = models.TextField(max_length=7, choices=AlertMode.choices, default=AlertMode.NEW)
    value = models.TextField(
        max_length=100,
        validators=[Validator(Regex.NAME.value, code="filter_value")],
        blank=True,
        null=True,
    )
    enabled = models.BooleanField(default=True)
    # Needs to be stored to automatically subscribe new project members
    subscribe_all_members = models.BooleanField(default=False)
    owner = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    subscribers = models.ManyToManyField(AUTH_USER_MODEL, related_name="alerts", blank=True)

    _project_field = "project"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["project", "item", "mode", "value"],
                name="unique_alerts_1",
                condition=models.Q(value__isnull=False),
            ),
            models.UniqueConstraint(
                fields=["project", "item", "mode"],
                name="unique_alerts_2",
                condition=models.Q(value__isnull=True),
            ),
        ]

    # The mapping below defines, for each alert item, the model it applies to,
    # the alert modes supported and for some items, a filter function.
    # This drives the logic in must_be_triggered and allows for flexible alert types.
    mapping = {
        AlertItem.OSINT: {"model": OSINT, AlertMode.NEW: True},
        AlertItem.HOST: {
            "model": Host,
            AlertMode.NEW: True,
            # For FILTER mode, use the 'ip' attribute of the finding
            AlertMode.FILTER: "ip",
        },
        AlertItem.OPEN_PORT: {
            "model": Port,
            # Only trigger for open ports
            "filter": lambda f: f.status == PortStatus.OPEN,
            AlertMode.NEW: True,
        },
        AlertItem.SERVICE: {
            "model": Port,
            # Only trigger if a service is detected on the port
            "filter": lambda f: f.service is not None,
            AlertMode.NEW: True,
            # For FILTER mode, use the 'service' attribute
            AlertMode.FILTER: "service",
        },
        AlertItem.TECHNOLOGY: {
            "model": Technology,
            AlertMode.NEW: True,
            # For FILTER mode, use the 'name' attribute
            AlertMode.FILTER: "name",
        },
        AlertItem.CREDENTIAL: {"model": Credential, AlertMode.NEW: True},
        AlertItem.VULNERABILITY: {
            "model": Vulnerability,
            AlertMode.NEW: True,
        },
        AlertItem.CVE: {
            "model": Vulnerability,
            # Only trigger if the finding has a CVE assigned
            "filter": lambda f: f.cve is not None,
            AlertMode.NEW: True,
            # For FILTER mode, use the 'cve' attribute
            AlertMode.FILTER: "cve",
            # For MONITOR mode, use the 'trending' attribute
            AlertMode.MONITOR: "trending",
        },
    }

    def __str__(self) -> str:
        """Return string representation of the alert.

        Returns:
            A string in format "project - mode - item - value".
        """
        values = [self.project.__str__(), self.mode, self.item]
        if self.value:
            values.append(self.value)
        return " - ".join(values)

    def must_be_triggered(self, execution: Execution, finding: Finding) -> bool:
        """Determine if this alert should be triggered for a given finding.

        Args:
            execution: The execution that produced the finding
            finding: The finding to evaluate against this alert

        Returns:
            True if the alert should be triggered, False otherwise
        """
        _mode = AlertMode(self.mode)
        data = self.mapping[AlertItem(self.item)]
        # Check if the finding is of the correct model type, is not fixed,
        # is not a false positive, and passes any custom filter (if present).
        if (
            not isinstance(finding, data["model"])
            or finding.is_fixed
            or (hasattr(finding, "triage_status") and finding.triage_status == TriageStatus.FALSE_POSITIVE)
            or not data.get(_mode)
            or (data.get("filter") and not data["filter"](finding))
        ):
            return False
        # The following logic determines which alert mode applies:
        # - NEW: Only trigger if this is the first execution for the finding
        # - FILTER: Trigger if the finding's attribute matches the alert's value
        # - MONITOR: Trigger if the finding's attribute (e.g., 'trending') is True
        return (
            (_mode == AlertMode.NEW and not finding.executions.exclude(id=execution.id).exists())
            or (
                _mode == AlertMode.FILTER
                and getattr(finding, str(data.get(AlertMode.FILTER, "")).lower()) == self.value.lower()
            )
            or (_mode == AlertMode.MONITOR and getattr(finding, str(data.get(AlertMode.MONITOR, "")).lower()) is True)
        )


class MonitorSettings(BaseModel):
    """Model for configuring automated monitoring jobs.

    This model stores configuration for background monitoring tasks that
    periodically check for trending vulnerabilities and security events.

    Attributes:
        rq_job_id: ID of the current monitoring job in the queue
        last_monitor: Timestamp of the last monitoring run
        hour_span: Hours between monitoring runs (24-168 hours)
    """

    rq_job_id = models.TextField(max_length=50, blank=True, null=True)
    last_monitor = models.DateTimeField(blank=True, null=True)
    hour_span = models.IntegerField(default=24, validators=[MinValueValidator(24), MaxValueValidator(168)])

    def __str__(self) -> str:
        """Return string representation of monitor settings.

        Returns:
            A string describing the last monitor time and next scheduled run.
        """
        return f"Last monitor was at {self.last_monitor}. Next one in {self.hour_span} hours"
