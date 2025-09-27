"""Enumeration classes for framework input keyword mappings.

Defines input keywords used for parsing and mapping data between
security tools and Rekono's internal data structures.
"""

from enum import Enum


class InputKeyword(Enum):
    """Enumeration of input keywords for tool argument mapping.

    Defines standardized keywords used to map data from Rekono's internal
    models to security tool arguments. Each keyword represents a specific
    type of input data that can be passed to security tools.

    Attributes:
        TARGET (int): Primary target identifier (IP, domain, URL).
        HOST (int): Host or server identifier.
        PORT (int): Single port number.
        PORTS (int): Multiple port numbers.
        PORTS_COMMAS (int): Comma-separated port list.
        TECHNOLOGY (int): Technology or software identifier.
        VERSION (int): Version information.
        ENDPOINT (int): API endpoint or path.
        URL (int): Complete URL with protocol.
        EMAIL (int): Email address.
        USERNAME (int): Username for authentication.
        SECRET (int): Password or secret value.
        CVE (int): CVE identifier for vulnerabilities.
        EXPLOIT (int): Exploit reference or identifier.
        WORDLIST (int): Wordlist file path.
        COOKIE_NAME (int): HTTP cookie name.
        TOKEN (int): Authentication token.
        CREDENTIAL_TYPE (int): Type of credential.
        CREDENTIAL_TYPE_LOWER (int): Lowercase credential type.
        HEADERS (int): HTTP headers collection.
        HEADER_KEY (int): Individual HTTP header name.
        HEADER_VALUE (int): Individual HTTP header value.
    """

    TARGET = 1
    HOST = 2
    PORT = 3
    PORTS = 4
    PORTS_COMMAS = 5
    TECHNOLOGY = 6
    VERSION = 7
    ENDPOINT = 8
    URL = 9
    EMAIL = 10
    USERNAME = 11
    SECRET = 12
    CVE = 13
    EXPLOIT = 14
    WORDLIST = 15
    COOKIE_NAME = 16
    TOKEN = 17
    CREDENTIAL_TYPE = 18
    CREDENTIAL_TYPE_LOWER = 19
    HEADERS = 20
    HEADER_KEY = 21
    HEADER_VALUE = 22
