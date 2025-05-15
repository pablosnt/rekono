# from enum import Enum  # https://github.com/google/pytype/issues/1048

from django.db.models import TextChoices


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
