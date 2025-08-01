"""Django app configuration for the findings module.

This app manages security findings discovered during security assessments,
including hosts, ports, vulnerabilities, credentials, and other
security-related data.
"""

from django.apps import AppConfig

from framework.apps import BaseApp


class FindingsConfig(BaseApp, AppConfig):
    """Django app configuration for the findings module.

    This app manages security findings discovered during security assessments,
    including hosts, ports, vulnerabilities, credentials, and other
    security-related data.
    """

    name = "findings"
