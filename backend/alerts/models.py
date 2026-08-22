"""Model of the alerts that notify the users about the findings."""

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
    """Rule that notifies some users when a finding is discovered in a project.

    Attributes:
        project: Project whose findings the alert watches.
        item: Kind of finding that triggers the alert.
        value: Value that the finding must have to trigger the alert, so an alert
          can watch one specific host or CVE instead of all of them.
        enabled: Whether the alert triggers notifications or not.
        subscribe_all_members: Whether the new members of the project must be
          subscribed to the alert, which is why it's stored instead of being
          applied only when the alert is created.
        owner: User that created the alert.
        subscribers: Users that are notified when the alert is triggered.
        mapping: Finding model that each item watches, with the condition that the
          finding must meet and the field that the alert value is compared to.
    """

    project = models.ForeignKey(Project, related_name="alerts", on_delete=models.CASCADE)
    item = models.TextField(max_length=15, choices=AlertItem.choices)
    value = models.TextField(
        max_length=100, validators=[Validator(Regex.NAME, code="filter_value")], blank=True, null=True
    )
    enabled = models.BooleanField(default=True)
    subscribe_all_members = models.BooleanField(default=False)
    owner = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    subscribers = models.ManyToManyField(AUTH_USER_MODEL, related_name="alerts", blank=True)

    _project_field = "project"

    class Meta:
        """Model configuration, allowing only one alert per item in a project."""

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

    mapping = {
        AlertItem.OSINT: {"model": OSINT},
        AlertItem.HOST: {"model": Host, "field": "ip"},
        AlertItem.OPEN_PORT: {
            "model": Port,
            "filter": lambda f: f.status == PortStatus.OPEN,
        },
        AlertItem.SERVICE: {
            "model": Port,
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
            "filter": lambda f: f.cve is not None,
            "field": "cve",
        },
        AlertItem.TRENDING_CVE: {
            "model": Vulnerability,
            "filter": lambda f: f.cve is not None,
            "field": "trending",
        },
    }

    def __str__(self) -> str:
        """Return the project and the item of the alert, with its value if it has one."""
        values = [self.project.__str__(), self.item]
        if self.value:
            values.append(self.value)
        return " - ".join(values)

    def must_be_triggered(self, execution: Execution, finding: Finding) -> bool:
        """Check if a finding discovered by an execution triggers this alert.

        Args:
            execution: Execution that discovered the finding, which is not needed
              for the trending CVE alerts.
            finding: Finding to check against the alert.

        Returns:
            Whether the finding is what the alert watches, and whether it's worth
            notifying: the findings that are fixed, discarded by the auditors, or
            created by the users never trigger an alert.
        """
        data = self.mapping[AlertItem(self.item)]
        if (
            finding.created_from_user_input
            or not isinstance(finding, data["model"])
            or finding.is_fixed
            or (hasattr(finding, "triage_status") and finding.triage_status == TriageStatus.FALSE_POSITIVE)
            or (data.get("filter") and not data["filter"](finding))
        ):
            return False
        # An alert is only triggered the first time that a finding is discovered, except for the
        # trending CVEs, since a CVE can start trending long after the vulnerability was found
        return (
            not self.value
            or (self.value and (str(getattr(finding, data.get("field", "")) or "")).lower()) == self.value.lower()
        ) and (self.item == AlertItem.TRENDING_CVE or not finding.executions.exclude(id=execution.id).exists())
