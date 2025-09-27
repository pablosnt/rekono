"""Settings models for Rekono.

This module defines the core Settings model that manages global configuration
parameters for the Rekono security platform. It provides centralized control
over system-wide settings including network proxy configuration, file upload
limits, and security policy controls.
"""

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from framework.models import BaseModel
from security.validators.input_validator import Regex, Validator


class Settings(BaseModel):
    """Global configuration model for Rekono platform settings.

    This model stores system-wide configuration parameters that control various
    aspects of the Rekono security platform behavior. Settings are managed as
    singleton instances with secure validation and administrative access controls.

    The Settings model provides centralized management for network proxy configuration,
    file upload constraints, and security policy controls that affect the entire
    platform operation.

    Attributes:
        max_uploaded_file_mb (IntegerField): Maximum size limit for file uploads in megabytes.
            Valid range: 128-3072 MB. Prevents resource exhaustion attacks.
        all_proxy (TextField): Global proxy server configuration for all protocols.
            Optional field with target format validation.
        http_proxy (TextField): HTTP protocol specific proxy server configuration.
            Optional field with target format validation.
        https_proxy (TextField): HTTPS protocol specific proxy server configuration.
            Optional field with target format validation.
        ftp_proxy (TextField): FTP protocol specific proxy server configuration.
            Optional field with target format validation.
        no_proxy (TextField): Comma-separated list of hosts to bypass proxy settings.
            Optional field with target format validation.
        auto_fix_findings (BooleanField): Enable automatic vulnerability remediation.
            Controls whether the platform attempts automated finding corrections.

    Example:
        Create a new security testing project:

        ```python
        settings = Settings.objects.create(
            max_uploaded_file_mb=1024,
            http_proxy="http://proxy.company.com:8080",
            auto_fix_findings=True
        )
        ```
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
