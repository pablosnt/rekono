"""Model of the Rekono configuration."""

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from framework.models import BaseModel
from security.validators.input_validator import Regex, Validator


class Settings(BaseModel):
    """Configuration of Rekono, of which only one instance exists.

    Attributes:
        max_uploaded_file_mb: Biggest file that the users can upload, in megabytes.
        all_proxy: Proxy that the tools use for all the protocols.
        http_proxy: Proxy that the tools use for HTTP.
        https_proxy: Proxy that the tools use for HTTPS.
        ftp_proxy: Proxy that the tools use for FTP.
        no_proxy: Hosts that the tools reach without going through the proxies.
        auto_fix_findings: Whether the findings that stop being discovered are
          fixed, and the fixed ones that appear again are reopened.
    """

    max_uploaded_file_mb = models.IntegerField(
        default=512, validators=[MinValueValidator(128), MaxValueValidator(3072)]
    )
    all_proxy = models.TextField(max_length=300, validators=[Validator(Regex.TARGET_REGEX)], blank=True, null=True)
    http_proxy = models.TextField(max_length=300, validators=[Validator(Regex.TARGET_REGEX)], blank=True, null=True)
    https_proxy = models.TextField(max_length=300, validators=[Validator(Regex.TARGET_REGEX)], blank=True, null=True)
    ftp_proxy = models.TextField(max_length=300, validators=[Validator(Regex.TARGET_REGEX)], blank=True, null=True)
    no_proxy = models.TextField(max_length=300, validators=[Validator(Regex.TARGET_REGEX)], blank=True, null=True)
    auto_fix_findings = models.BooleanField(default=True)
