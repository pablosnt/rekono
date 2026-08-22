"""Django app configuration of the tools app."""

from django.apps import AppConfig

from framework.apps import BaseApp


class ToolsConfig(BaseApp, AppConfig):
    """Configuration of the tools app.

    Attributes:
        name: Name of the app in the Django app registry.
    """

    name = "tools"

    def _clear_before_load(self) -> None:
        """Delete everything that the fixtures create again on every migration.

        These entities only relate to the tools and the configurations, and nothing
        outside the catalog references them, so they are recreated freely, letting
        maintainers reorder them in the most convenient way. The tools and the
        configurations themselves are created by the migrations instead, since the
        processes, the tasks and the executions do reference them.
        """
        from tools.models import Argument, Input, Intensity, Output

        for model in [Intensity, Argument, Input, Output]:
            model.objects.all().delete()
