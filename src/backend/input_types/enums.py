"""Input type name enumerations for defining available input models categories.

This module defines the InputTypeName enum which contains all the valid input
type names that can be used in the InputType model. These names represent
different categories of data that can be provided as input to tools during
execution.
"""

from django.db.models import TextChoices
from django.db.models.enums import Choices


class InputTypeName(TextChoices):
    """Enumeration of valid input type names for tool execution.

    This enum defines all the different categories of input models that can be
    provided to tools. Each choice represents a specific type of data that
    tools can process and use during their execution.

    The choices include various data types such as OSINT information, host
    details, port information, file paths, technology stacks, credentials,
    vulnerabilities, exploits, wordlists, authentication data, and HTTP
    headers.
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
