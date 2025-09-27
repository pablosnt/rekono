"""Django app configuration for the findings module.

Configures the findings Django app providing comprehensive management of
security findings discovered during automated assessments with complete
lifecycle support from discovery through triage and reporting.
"""

from django.apps import AppConfig

from framework.apps import BaseApp


class FindingsConfig(BaseApp, AppConfig):
    """Django app configuration for findings module.

    Configures the findings application for security assessment results
    management including discovery, vulnerability identification, credential
    exposure detection, and exploit tracking with triage workflows.

    Attributes:
        name (str): The name of the Django app
    """

    name = "findings"
