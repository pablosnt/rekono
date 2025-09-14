"""Django app configuration for statistics and analytics module."""

from django.apps import AppConfig

from framework.apps import BaseApp


class StatsConfig(BaseApp, AppConfig):
    """App configuration for statistics and analytics functionality.
    
    Provides Django app configuration for the statistics module including
    app metadata and initialization settings.
    """
    
    name = "stats"
