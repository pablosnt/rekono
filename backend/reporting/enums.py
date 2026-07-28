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

    Attributes:
        OSINT (str): Open Source Intelligence findings
        HOST (str): Host discovery findings
        PORT (str): Open port findings
        PATH (str): Web path and resource findings
        TECHNOLOGY (str): Technology identification findings
        CREDENTIAL (str): Credential discovery findings
        VULNERABILITY (str): General vulnerability findings
        EXPLOIT (str): Exploit availability findings
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

    Attributes:
        JSON (str): JSON output format
        XML (str): XML output format
        PDF (str): PDF output format
    """

    JSON = "json"
    XML = "xml"
    PDF = "pdf"


class ReportStatus(TextChoices):
    """Enumeration of report generation status values.

    Defines the possible status values during the report generation
    lifecycle from creation to completion.

    Attributes:
        READY (str): Report generated and available for download
        PENDING (str): Report generation in progress
        ERROR (str): Report generation failed
    """

    READY = "Ready"
    PENDING = "Pending"
    ERROR = "Error"


# Type annotation workaround for pytype compatibility
# See: https://github.com/google/pytype/issues/1048
FindingName: type[Choices] = FindingName
ReportFormat: type[Choices] = ReportFormat
ReportStatus: type[Choices] = ReportStatus
