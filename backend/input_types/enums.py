"""Names of the input types that the tools can take as arguments."""

from django.db.models import TextChoices
from django.db.models.enums import Choices


class InputTypeName(TextChoices):
    """Name of one kind of data that a tool argument takes.

    Most of the names match a finding type, since the tools mainly work with what
    the previous executions discovered, and the rest match the resources that the
    users create, like the wordlists or the authentications.
    """

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


# Type annotation workaround for pytype compatibility
# See: https://github.com/google/pytype/issues/1048
InputTypeName: type[Choices] = InputTypeName
