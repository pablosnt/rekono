from enum import Enum


class InputKeyword(Enum):
    """Enumeration of keywords that can be used on command templates.

    This enum defines the standard keywords used for identifying and
    categorizing different types of input data that will be used as part
    of tool executions.
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
