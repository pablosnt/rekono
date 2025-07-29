"""Enums for alert configuration and management.

This module defines the enumeration classes used throughout the alerts system
to specify alert types, modes, and other configuration options.
"""

from django.db.models import TextChoices
from django.db.models.enums import Choices


class AlertItem(TextChoices):
    """Enumeration of alert item types.

    Defines the different types of findings that can trigger alerts in the
    Rekono platform.

    Attributes:
        OSINT: Open Source Intelligence findings
        HOST: Host discovery findings
        OPEN_PORT: Open port findings
        SERVICE: Service detection findings
        TECHNOLOGY: Technology identification findings
        CREDENTIAL: Credential discovery findings
        VULNERABILITY: General vulnerability findings
        CVE: Common Vulnerabilities and Exposures findings
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
    """Enumeration of alert modes.

    Defines the different ways alerts can be configured to trigger.

    Attributes:
        NEW: Alert triggers when a new finding is discovered
        FILTER: Alert triggers when a finding matches specific criteria
        MONITOR: Alert triggers for monitoring trending or status changes
    """

    NEW = "New"
    FILTER = "Filter"
    MONITOR = "Monitor"


# The following assignments are a workaround for a known issue with Google Pytype static analysis.
# See: https://github.com/google/pytype/issues/1048
# Without these, Pytype may not recognize the TextChoices subclasses as valid Choices types.
AlertItem: type[Choices] = AlertItem
AlertMode: type[Choices] = AlertMode
