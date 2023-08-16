from django.db import models


class InputTypeName(models.TextChoices):
    """Input type names, related to findings and wordlists."""

    OSINT = "OSINT"
    HOST = "Host"
    PORT = "Port"
    PATH = "Path"
    TECHNOLOGY = "Technology"
    VULNERABILITY = "Vulnerability"
    EXPLOIT = "Exploit"
    CREDENTIAL = "Credential"
    WORDLIST = "Wordlist"
    AUTHENTICATION = "Authentication"
