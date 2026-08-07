"""Keywords available to build the arguments of the tool executions.

The input models of Rekono (targets, findings, credentials, wordlists, and HTTP
headers) provide their data using these keywords, and the tool configurations
reference them from their argument templates.
"""

from enum import Enum


class InputKeyword(Enum):
    """Placeholder that can be used in the argument templates of a tool configuration.

    The lowercase member name is the placeholder written between braces in the
    argument, like ``-p {ports}``, and each input model fills the keywords it can
    provide. A few keywords are just formatting variants: PORTS_COMMAS joins the
    ports with commas, and CREDENTIAL_TYPE_LOWER lowercases the credential type.
    HEADERS is the exception, since it holds all the HTTP headers at once and its
    argument is formatted once per header using HEADER_KEY and HEADER_VALUE.
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
