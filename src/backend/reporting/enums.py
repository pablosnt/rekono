from django.db.models import TextChoices
from django.db.models.enums import Choices


class FindingName(TextChoices):
    OSINT = "OSINT"
    HOST = "Host"
    PORT = "Port"
    PATH = "Path"
    TECHNOLOGY = "Technology"
    CREDENTIAL = "Credential"
    VULNERABILITY = "Vulnerability"
    EXPLOIT = "Exploit"


class ReportFormat(TextChoices):
    JSON = "json"
    XML = "xml"
    PDF = "pdf"


class ReportStatus(TextChoices):
    READY = "Ready"
    PENDING = "Pending"
    ERROR = "Error"


# https://github.com/google/pytype/issues/1048
FindingName: type[Choices] = FindingName
ReportFormat: type[Choices] = ReportFormat
ReportStatus: type[Choices] = ReportStatus
