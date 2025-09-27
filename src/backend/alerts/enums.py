"""Enums for alert configuration and management.

Defines enumeration classes for alert types, modes, and configuration options
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
    """

    OSINT = "OSINT"
    HOST = "Host"
    OPEN_PORT = "Open Port"
    SERVICE = "Service"
    TECHNOLOGY = "Technology"
    CREDENTIAL = "Credential"
    VULNERABILITY = "Vulnerability"
    CVE = "CVE"


class AlertMode(TextChoices):
    """Enumeration of alert trigger modes.

    Defines how alerts can be configured to trigger based on findings.

    Attributes:
        NEW (str): Alert triggers when a new finding is discovered
        FILTER (str): Alert triggers when a finding matches specific criteria
        MONITOR (str): Alert triggers for trending or status changes
    """

    NEW = "New"
    FILTER = "Filter"
    MONITOR = "Monitor"


# Type annotation workaround for pytype compatibility
# See: https://github.com/google/pytype/issues/1048
AlertItem: type[Choices] = AlertItem
AlertMode: type[Choices] = AlertMode
