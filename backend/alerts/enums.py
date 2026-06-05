"""Enums for alert configuration and management.

Defines enumeration classes for alert types and configuration options
used throughout the alerts system.
"""

from django.db.models import TextChoices
from django.db.models.enums import Choices


class AlertItem(TextChoices):
    """Enumeration of alert item types.

    Defines the types of security findings that can trigger alerts.

    Attributes:
        OSINT (str): Open Source Intelligence findings
        HOST (str): Host discovery findings
        OPEN_PORT (str): Open port findings
        SERVICE (str): Service detection findings
        TECHNOLOGY (str): Technology identification findings
        CREDENTIAL (str): Credential discovery findings
        VULNERABILITY (str): General vulnerability findings
        CVE (str): Common Vulnerabilities and Exposures findings
        TRENDING_CVE (str): Trending CVE findings from monitoring
    """

    OSINT = "OSINT"
    HOST = "Host"
    OPEN_PORT = "Open Port"
    SERVICE = "Service"
    TECHNOLOGY = "Technology"
    CREDENTIAL = "Credential"
    VULNERABILITY = "Vulnerability"
    CVE = "CVE"
    TRENDING_CVE = "Trending CVE"


# Type annotation workaround for pytype compatibility
# See: https://github.com/google/pytype/issues/1048
AlertItem: type[Choices] = AlertItem
