"""Django models for alert management.

This module provides the core data model for Rekono's alerting system, which
enables security teams to receive real-time notifications about security findings.
Alerts support both immediate triggers and trending CVE monitoring mode, with
flexible filtering capabilities to reduce noise and focus on relevant threats.

Key Components:
    Alert: Configurable alert rules that trigger notifications based on finding types,
           monitoring mode, and custom filters. Supports project-level alerting with
           fine-grained subscriber management.

Architecture:
    The alerting system uses a mapping-based approach where each alert item type
    (OSINT, hosts, ports, etc.) is mapped to specific Django models and supports
    both immediate alerts and trending CVE monitoring. This design allows for type-safe
    alert processing and easy extension for new finding types.
"""

from django.db import models

from alerts.enums import AlertItem
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
    security findings are discovered. Supports both immediate alerts and monitoring
    modes with filtering criteria to ensure relevant notifications.

    Attributes:
        project (ForeignKey): The project this alert belongs to
        item (TextField): The type of finding to monitor (from AlertItem enum)
        value (TextField): Optional filter value for filtered alerts
        enabled (BooleanField): Whether this alert is currently active
        subscribe_all_members (BooleanField): Auto-subscribe all project members
        owner (ForeignKey): The user who created this alert
        subscribers (ManyToManyField): Users subscribed to receive notifications
        mapping (dict): Maps each AlertItem to its target model and, optionally,
                       a filter function and the field used to match the alert value

    Example:
        Create an alert for new CVEs in a project:

        ```python
        Alert.objects.create(
            project=my_project,
            item=AlertItem.CVE,
            owner=request.user
        )
        ```
    """

    project = models.ForeignKey(Project, related_name="alerts", on_delete=models.CASCADE)
    item = models.TextField(max_length=15, choices=AlertItem.choices)
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
        """Meta configuration for the Alert model.

        Defines database constraints ensuring alert uniqueness per project, both
        for value-specific alerts and for value-less ones.

        Attributes:
            constraints (list): Uniqueness constraints for project/item/value combinations
        """

        constraints = [
            models.UniqueConstraint(
                fields=["project", "item", "value"],
                name="unique_alerts_1",
                condition=models.Q(value__isnull=False),
            ),
            models.UniqueConstraint(
                fields=["project", "item"],
                name="unique_alerts_2",
                condition=models.Q(value__isnull=True),
            ),
        ]

    # The mapping below defines, for each alert item, the model it applies to
    # and for some items, a filter function. Special handling is provided for
    # trending CVE alerts. This drives the logic in must_be_triggered.
    mapping = {
        AlertItem.OSINT: {"model": OSINT},
        AlertItem.HOST: {"model": Host, "field": "ip"},
        AlertItem.OPEN_PORT: {
            "model": Port,
            # Only trigger for open ports
            "filter": lambda f: f.status == PortStatus.OPEN,
        },
        AlertItem.SERVICE: {
            "model": Port,
            # Only trigger if a service is detected on the port
            "filter": lambda f: f.service is not None,
            "field": "service",
        },
        AlertItem.TECHNOLOGY: {
            "model": Technology,
            "field": "name",
        },
        AlertItem.CREDENTIAL: {"model": Credential},
        AlertItem.VULNERABILITY: {"model": Vulnerability},
        AlertItem.CVE: {
            "model": Vulnerability,
            # Only trigger if the finding has a CVE assigned
            "filter": lambda f: f.cve is not None,
            "field": "cve",
        },
        AlertItem.TRENDING_CVE: {
            "model": Vulnerability,
            # Only trigger if the finding has a CVE assigned
            "filter": lambda f: f.cve is not None,
            "field": "trending",
        },
    }

    def __str__(self) -> str:
        """Return string representation of the alert.

        Returns:
            str: The project, item type, and filter value (if set), joined by " - ".
        """
        values = [self.project.__str__(), self.item]
        if self.value:
            values.append(self.value)
        return " - ".join(values)

    def must_be_triggered(self, execution: Execution, finding: Finding) -> bool:
        """Determine if this alert should be triggered for a given finding.

        A finding must match the alert item's model type, must not be fixed,
        marked as a false positive, or created from user input, and must pass
        the item's custom filter (if any). If the alert has a filter value,
        the finding's mapped field must also match it case-insensitively.
        Trending CVE alerts are evaluated on their own, independently of any
        single execution, since they track CVE trends across the whole
        project. Every other alert only fires the first time a finding is
        seen, so execution is used to check that the finding has not already
        appeared in an earlier execution.

        Args:
            execution (Execution): The execution the finding was reported in.
                                   Not used for trending CVE alerts, so it may
                                   be None in that case.
            finding (Finding): The finding to evaluate against this alert.

        Returns:
            bool: True if the alert should be triggered, False otherwise.
        """
        data = self.mapping[AlertItem(self.item)]
        # Check if the finding is of the correct model type, is not fixed,
        # is not created from user input, is not a false positive, and
        # passes any custom filter (if present).
        if (
            finding.created_from_user_input
            or not isinstance(finding, data["model"])
            or finding.is_fixed
            or (hasattr(finding, "triage_status") and finding.triage_status == TriageStatus.FALSE_POSITIVE)
            or (data.get("filter") and not data["filter"](finding))
        ):
            return False
        return (
            not self.value
            or (self.value and (str(getattr(finding, data.get("field", "")) or "")).lower()) == self.value.lower()
        ) and (self.item == AlertItem.TRENDING_CVE or not finding.executions.exclude(id=execution.id).exists())
