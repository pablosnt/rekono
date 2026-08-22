"""Models of the DefectDojo configuration and of the synchronized projects.

Typical usage example:

  settings = DefectDojoSettings.objects.first()
  settings.secret = "..."  # encrypted into _api_token on save
  settings.save()
"""

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from framework.models import BaseEncrypted, BaseModel
from projects.models import Project
from security.validators.input_validator import Regex, Validator
from targets.models import Target


class DefectDojoSettings(BaseEncrypted):
    """Configuration of DefectDojo, of which only one instance exists.

    Attributes:
        server: URL of the DefectDojo server, since it's deployed by the users.
        tls_validation: Whether the TLS certificate of the server must be valid,
          which it isn't when DefectDojo is deployed with a self signed one.
        tag: Tag added to everything that Rekono creates in DefectDojo.
        date_format: Format that the server expects the dates in, which depends on
          how DefectDojo itself is configured.
    """

    server = models.TextField(max_length=100, validators=[Validator(Regex.TARGET)], blank=True, null=True)
    _api_token = models.TextField(
        max_length=40,
        validators=[Validator(Regex.SECRET, code="api_token")],
        null=True,
        blank=True,
        db_column="api_token",
    )
    tls_validation = models.BooleanField(default=True)
    tag = models.TextField(max_length=200, validators=[Validator(Regex.NAME, code="tag")], blank=True, null=True)
    date_format = models.TextField(max_length=15)

    _encrypted_field = "_api_token"

    def __str__(self) -> str:
        """Return the URL of the server, or the platform name if it isn't configured."""
        return self.server if self.server else super().__str__()


class DefectDojoSync(BaseModel):
    """Product of DefectDojo that the findings of a project are sent to.

    Attributes:
        project: Project whose findings are sent to DefectDojo.
        product_id: Product of DefectDojo that receives the findings.
        engagement_id: Engagement of that product that receives them, which is
          created per target if it isn't defined here.
        reimport: Whether the findings must be added to the test of the previous
          executions, instead of creating a new test for each execution.
        close_old_findings: Whether the findings of that test that an execution
          doesn't discover anymore must be closed.
    """

    project = models.OneToOneField(Project, related_name="defectdojo_sync", on_delete=models.CASCADE)
    product_id = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(999999999)],
        blank=True,
        null=True,
    )
    engagement_id = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(999999999)],
        blank=True,
        null=True,
    )
    reimport = models.BooleanField(default=False)
    close_old_findings = models.BooleanField(default=False)

    _project_field = "project"

    def __str__(self) -> str:
        """Return the project and where its findings are sent in DefectDojo."""
        return " - ".join([value.__str__() for value in [self.project, self.product_id, self.engagement_id] if value])


class DefectDojoTargetSync(BaseModel):
    """Engagement of DefectDojo that the findings of a target are sent to.

    Attributes:
        defectdojo_sync: Synchronization of the project that the target belongs to.
        target: Target whose findings are sent to the engagement.
        engagement_id: Engagement that receives the findings of the target.
    """

    defectdojo_sync = models.ForeignKey(DefectDojoSync, related_name="target_syncs", on_delete=models.CASCADE)
    target = models.OneToOneField(Target, related_name="defectdojo_sync", on_delete=models.CASCADE)
    engagement_id = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(999999999)])

    _project_field = "defectdojo_sync__project"

    def __str__(self) -> str:
        """Return the target and the engagement where its findings are sent."""
        return " - ".join([self.defectdojo_sync.__str__(), self.target.target, str(self.engagement_id)])
