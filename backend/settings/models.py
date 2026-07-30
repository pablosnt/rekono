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
            Defaults to 512 MB. Valid range: 128-3072 MB, enforced to prevent resource
            exhaustion attacks.
        all_proxy (TextField): Proxy server exported as the ALL_PROXY environment
            variable for tool execution (max 300 chars). Optional, blank and null allowed.
        http_proxy (TextField): Proxy server exported as the HTTP_PROXY environment
            variable for tool execution (max 300 chars). Optional, blank and null allowed.
        https_proxy (TextField): Proxy server exported as the HTTPS_PROXY environment
            variable for tool execution (max 300 chars). Optional, blank and null allowed.
        ftp_proxy (TextField): Proxy server exported as the FTP_PROXY environment
            variable for tool execution (max 300 chars). Optional, blank and null allowed.
        no_proxy (TextField): Hosts exported as the NO_PROXY environment variable
            to bypass proxying for tool execution (max 300 chars). Optional, blank
            and null allowed.
        auto_fix_findings (BooleanField): Whether findings are automatically reactivated
            when they reappear in a later execution and marked as fixed when they are
            no longer detected. Defaults to True.

    Example:
        Update the singleton settings instance created by the app's fixtures:

        ```python
        settings = Settings.objects.first()
        settings.http_proxy = "http://10.10.10.10:8080"
        settings.max_uploaded_file_mb = 1024
        settings.save()
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
