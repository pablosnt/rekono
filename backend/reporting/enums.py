"""Options that a report can be created with."""

from django.db.models import TextChoices
from django.db.models.enums import Choices


class FindingName(TextChoices):
    """Finding type that a report can include."""

    OSINT = "OSINT"
    HOST = "Host"
    PORT = "Port"
    PATH = "Path"
    TECHNOLOGY = "Technology"
    CREDENTIAL = "Credential"
    VULNERABILITY = "Vulnerability"
    EXPLOIT = "Exploit"


class ReportFormat(TextChoices):
    """Format that a report can be generated in.

    The value is also the extension of the generated file.
    """

    JSON = "json"
    XML = "xml"
    PDF = "pdf"


class ReportStatus(TextChoices):
    """State of the generation of a report."""

    READY = "Ready"
    PENDING = "Pending"
    ERROR = "Error"


# Type annotation workaround for pytype compatibility
# See: https://github.com/google/pytype/issues/1048
FindingName: type[Choices] = FindingName
ReportFormat: type[Choices] = ReportFormat
ReportStatus: type[Choices] = ReportStatus
