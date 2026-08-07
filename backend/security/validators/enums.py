"""Regex patterns shared by the Rekono validators."""

from enum import Enum


class Regex(Enum):
    """Regex pattern that a kind of value must match to be accepted.

    All of them describe an accepted shape, except INJECTION and SENSITIVE_ENV,
    which describe values that must be rejected.

    Attributes:
        IP_RANGE: Range of IP addresses, like 192.168.1.1-50.
        NAME: Name of an entity, including accented and punctuation characters.
        TEXT: Free text, excluding the characters used to inject HTML or commands.
        TARGET: IP address, IP range, domain, or URL that can be scanned.
        TARGET_REGEX: Deny list entry, which can also include regex metacharacters
          to deny several targets at once.
        PATH: File system or web path.
        PATH_WITH_QUERYPARAMS: Web path including its query parameters and fragment.
        CVE: CVE identifier in CVE-YYYY-NNNN form.
        SECRET: Credential value, which accepts most printable characters.
        INJECTION: Characters commonly used to inject commands or HTML.
        SENSITIVE_ENV: Environment variable assignments (PATH, LD_PRELOAD, and so
          on) that could hijack the subprocess of a tool execution.
    """

    IP_RANGE = r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}-\d{1,3}"
    NAME = r"[\wÀ-ÿ\s\.:\-\[\]()@]{0,120}"
    TEXT = r"[^;<>]*"
    TARGET = r"[\w\d\.:\-/]{1,100}"
    TARGET_REGEX = r"[\w\d\.,:\-/\*\?\+\(\)\\]{1,300}"
    PATH = r"[\w\.\-_/\\]{0,500}"
    PATH_WITH_QUERYPARAMS = r"[\w\.\-_/\\#?&%$]{0,500}"
    CVE = r"CVE-\d{4}-\d{1,10}"
    SECRET = r"[\w \t\./\-=\+,:<>¿?¡!#&$()@%\[\]\{\}\*]{1,500}"
    INJECTION = r"[;\"'&<>$]+"
    SENSITIVE_ENV = r".*(PATH|IFS|ENV|BASH_ENV|SHELLOPTS|PS4|PYTHONPATH|PYTHONSTARTUP|PYTHONHOME|PERL5LIB|PERLLIB|RUBYLIB|RUBYOPT|NODE_OPTIONS|NODE_PATH|LD_[A-Z_]+|DYLD_[A-Z_]+)\s*=?.*"
