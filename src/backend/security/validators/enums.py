"""Enumeration definitions for security validation patterns.

Provides regex pattern enumerations for input validation and security
controls across the Rekono platform.
"""

from enum import Enum


class Regex(Enum):
    """Enumeration of regex patterns for input validation.

    Provides regex patterns for validating user input and implementing
    security controls to prevent injection attacks and ensure data integrity.

    Attributes:
        IP_RANGE (str): Validates IP address ranges (e.g., 192.168.1.1-50)
        NAME (str): General name fields with international character support
        TEXT (str): Safe text content excluding dangerous characters
        TARGET (str): Security testing target validation (IPs, domains, paths)
        TARGET_REGEX (str): Extended target patterns with regex metacharacters
        PATH (str): File and directory path validation
        PATH_WITH_QUERYPARAMS (str): Web paths including query parameters
        CVE (str): Common Vulnerabilities and Exposures identifier format
        SECRET (str): Secure credential and password validation
        INJECTION (str): Pattern to detect common injection attack vectors
    """

    IP_RANGE = r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}-\d{1,3}"
    NAME = r"[\wÀ-ÿ\s\.:\-\[\]()@]{0,120}"
    TEXT = r"[^;<>]*"
    TARGET = r"[\w\d\.:\-/]{1,100}"
    TARGET_REGEX = r"[\w\d\.,:\-/\*\?\+\(\)\\]{1,300}"
    PATH = r"[\w\.\-_/\\]{0,500}"
    PATH_WITH_QUERYPARAMS = r"[\w\.\-_/\\#?&%$]{0,500}"
    CVE = r"CVE-\d{4}-\d{1,7}"
    SECRET = r"[\w\s\./\-=\+,:<>¿?¡!#&$()@%\[\]\{\}\*]{1,500}"
    INJECTION = r"[;\"'&<>$]+"
