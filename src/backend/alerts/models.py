"""Django models for alert management and monitoring.

This module provides the core data models for Rekono's alerting system,
which enables security teams to receive real-time notifications about security findings.
The alerting system supports multiple notification modes and flexible filtering
capabilities to reduce noise and focus on relevant threats.

Key Components:
    Alert: Configurable alert rules that trigger notifications based on finding types,
           discovery modes, and custom filters. Supports project-level alerting with
           fine-grained subscriber management.
    MonitorSettings: Configuration for automated background monitoring jobs that
                    periodically check for trending vulnerabilities and security events.

Architecture:
    The alerting system uses a mapping-based approach where each alert item type
    (OSINT, hosts, ports, etc.) is mapped to specific Django models and supported
    alert modes. This design allows for type-safe alert processing and easy extension
    for new finding types.
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
    """Model for configuring security alert rules.

    Represents an alert configuration that triggers notifications when specific
    security findings are discovered. Supports multiple trigger modes and filtering
    criteria to ensure relevant notifications.

    Attributes:
        project (ForeignKey): The project this alert belongs to
        item (TextField): The type of finding to monitor (from AlertItem enum)
        mode (TextField): How the alert triggers (from AlertMode enum)
        value (TextField): Optional filter value for FILTER mode alerts
        enabled (BooleanField): Whether this alert is currently active
        subscribe_all_members (BooleanField): Auto-subscribe all project members
        owner (ForeignKey): The user who created this alert
        subscribers (ManyToManyField): Users subscribed to receive notifications

    Example:
        Create an alert for new CVEs in a project:

        ```python
        Alert.objects.create(
            project=my_project,
            item=AlertItem.CVE,
            mode=AlertMode.NEW,
            owner=request.user
        )
        ```
    """

    project = models.ForeignKey(Project, related_name="alerts", on_delete=models.CASCADE)
    item = models.TextField(max_length=15, choices=AlertItem.choices)
    mode = models.TextField(max_length=7, choices=AlertMode.choices, default=AlertMode.NEW)
    value = models.TextField(
        max_length=100, validators=[Validator(Regex.NAME, code="filter_value")], blank=True, null=True
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
            str: A string in format "project - mode - item - value".
        """
        values = [self.project.__str__(), self.mode, self.item]
        if self.value:
            values.append(self.value)
        return " - ".join(values)

    def must_be_triggered(self, execution: Execution, finding: Finding) -> bool:
        """Determine if this alert should be triggered for a given finding.

        Evaluates whether a finding should trigger this alert based on:
        - Finding type matches alert item type
        - Finding is not fixed or marked as false positive
        - Alert mode conditions are met (NEW/FILTER/MONITOR)
        - Custom filter functions pass (if defined)

        Args:
            execution (Execution): The execution that produced the finding
            finding (Finding): The finding to evaluate against this alert

        Returns:
            bool: True if the alert should be triggered, False otherwise
        """
        _mode = AlertMode(self.mode)
        data = self.mapping[AlertItem(self.item)]
        # Check if the finding is of the correct model type, is not fixed,
        # is not a false positive, and passes any custom filter (if present).
        if (
            finding.created_from_user_input
            or not isinstance(finding, data["model"])
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
    """Model for configuring automated threat intelligence monitoring.

    Manages configuration for background monitoring jobs that periodically query
    external threat intelligence sources.
    Follows a singleton pattern - only one instance should exist.

    The monitoring system schedules itself using RQ jobs and triggers MONITOR
    mode alerts when needed.

    Attributes:
        rq_job_id (TextField): ID of the current scheduled monitoring job
        last_monitor (DateTimeField): Timestamp of the last monitoring execution
        hour_span (IntegerField): Hours between monitoring runs (24-168 hours)

    Example:
        Configure monitoring to run every 48 hours:

        ```python
        settings = MonitorSettings.objects.first()
        settings.hour_span = 48
        settings.save()
        ```
    """

    rq_job_id = models.TextField(max_length=50, blank=True, null=True)
    last_monitor = models.DateTimeField(blank=True, null=True)
    hour_span = models.IntegerField(default=24, validators=[MinValueValidator(24), MaxValueValidator(168)])

    def __str__(self) -> str:
        """Return string representation of monitor settings.

        Returns:
            str: Description of last monitor time and next scheduled run
        """
        return f"Last monitor was at {self.last_monitor}. Next one in {self.hour_span} hours"
