from django.db.models import TextChoices
from django.db.models.enums import Choices


class InputTypeName(TextChoices):
    OSINT = "OSINT"
    HOST = "Host"
    PORT = "Port"
    PATH = "Path"
    TECHNOLOGY = "Technology"
    CREDENTIAL = "Credential"
    VULNERABILITY = "Vulnerability"
    EXPLOIT = "Exploit"
    WORDLIST = "Wordlist"
    AUTHENTICATION = "Authentication"
    HTTP_HEADER = "Http Header"


InputTypeName: type[Choices] = InputTypeName  # https://github.com/google/pytype/issues/1048
