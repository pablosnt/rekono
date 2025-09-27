"""Input type name enumerations for defining available input data categories.

This module defines the InputTypeName enum which contains all the valid input
type names that can be used in the InputType model for security tool integration.
"""

from django.db.models import TextChoices
from django.db.models.enums import Choices


class InputTypeName(TextChoices):
    """Enumeration of valid input type names for security tool execution.

    This enum defines all the different categories of input data that can be
    provided to security tools during execution, supporting various data types
    for comprehensive security testing workflows.

    Attributes:
        OSINT (str): Open source intelligence data.
        HOST (str): Network host information.
        PORT (str): Network port and service data.
        PATH (str): File paths and web endpoints.
        TECHNOLOGY (str): Technology stack information.
        CREDENTIAL (str): Authentication credentials.
        VULNERABILITY (str): Security vulnerability data.
        EXPLOIT (str): Exploit and proof-of-concept data.
        WORDLIST (str): Wordlist and dictionary data.
        AUTHENTICATION (str): Authentication configuration.
        HTTP_HEADER (str): HTTP header information.
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
