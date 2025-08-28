"""Enumeration classes for reporting module configuration and choices.

Defines enumeration classes for report formats, finding types, and status
values used throughout the reporting system for consistent data handling.
"""

from django.db.models import TextChoices
from django.db.models.enums import Choices


class FindingName(TextChoices):
    """Enumeration of security finding types available for report generation.

    Defines the types of security findings that can be included in reports
    with standardized naming for consistent data processing.
    """
    OSINT = "OSINT"
    HOST = "Host"
    PORT = "Port"
    PATH = "Path"
    TECHNOLOGY = "Technology"
    CREDENTIAL = "Credential"
    VULNERABILITY = "Vulnerability"
    EXPLOIT = "Exploit"


class ReportFormat(TextChoices):
    """Enumeration of supported report output formats.

    Defines the available output formats for security report generation
    with corresponding file extensions.
    """
    JSON = "json"
    XML = "xml"
    PDF = "pdf"


class ReportStatus(TextChoices):
    """Enumeration of report generation status values.

    Defines the possible status values during the report generation
    lifecycle from creation to completion.
    """
    READY = "Ready"
    PENDING = "Pending"
    ERROR = "Error"


# Type annotation workaround for pytype compatibility
# See: https://github.com/google/pytype/issues/1048
FindingName: type[Choices] = FindingName
ReportFormat: type[Choices] = ReportFormat
ReportStatus: type[Choices] = ReportStatus
