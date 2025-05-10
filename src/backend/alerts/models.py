from alerts.enums import AlertItem, AlertMode
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
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

# Create your models here.


class Alert(BaseModel):
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
    subscribe_all_members = models.BooleanField(default=False)
    owner = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    subscribers = models.ManyToManyField(AUTH_USER_MODEL, related_name="alerts", blank=True)

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

    mapping = {
        AlertItem.OSINT.value: {"model": OSINT, AlertMode.NEW.value: True},
        AlertItem.HOST.value: {
            "model": Host,
            AlertMode.NEW.value: True,
            AlertMode.FILTER.value: "ip",
        },
        AlertItem.OPEN_PORT.value: {
            "model": Port,
            "filter": lambda f: f.status == PortStatus.OPEN,
            AlertMode.NEW.value: True,
        },
        AlertItem.SERVICE.value: {
            "model": Port,
            "filter": lambda f: f.service is not None,
            AlertMode.NEW.value: True,
            AlertMode.FILTER.value: "service",
        },
        AlertItem.TECHNOLOGY.value: {
            "model": Technology,
            AlertMode.NEW.value: True,
            AlertMode.FILTER.value: "name",
        },
        AlertItem.CREDENTIAL.value: {"model": Credential, AlertMode.NEW.value: True},
        AlertItem.VULNERABILITY.value: {
            "model": Vulnerability,
            AlertMode.NEW.value: True,
        },
        AlertItem.CVE.value: {
            "model": Vulnerability,
            "filter": lambda f: f.cve is not None,
            AlertMode.NEW.value: True,
            AlertMode.FILTER.value: "cve",
            AlertMode.MONITOR.value: "trending",
        },
    }

    def __str__(self) -> str:
        values = [self.project.__str__(), self.mode, self.item]
        if self.value:
            values.append(self.value)
        return " - ".join(values)

    @classmethod
    def get_project_field(cls) -> str:
        return "project"

    def must_be_triggered(self, execution: Execution, finding: Finding) -> bool:
        data = self.mapping[self.item]
        if (
            not isinstance(finding, data["model"])
            or finding.is_fixed
            or (hasattr(finding, "triage_status") and finding.triage_status == TriageStatus.FALSE_POSITIVE)
            or not data.get(self.mode)
            or (data.get("filter") and not data["filter"](finding))
        ):
            return False
        if self.mode == AlertMode.NEW.value:
            return not finding.executions.exclude(id=execution.id).exists()
        elif self.mode == AlertMode.FILTER.value:
            return getattr(finding, data.get(AlertMode.FILTER.value, "").lower()) == self.value.lower()
        else:
            return getattr(finding, data.get(AlertMode.MONITOR.value, "").lower()) is True


class MonitorSettings(BaseModel):
    rq_job_id = models.TextField(max_length=50, blank=True, null=True)
    last_monitor = models.DateTimeField(blank=True, null=True)
    hour_span = models.IntegerField(default=24, validators=[MinValueValidator(24), MaxValueValidator(168)])

    def __str__(self) -> str:
        return f"Last monitor was at {self.last_monitor}. Next one in {self.hour_span} hours"
