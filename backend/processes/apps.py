"""Django app configuration of the processes app."""

from typing import Any

from django.apps import AppConfig
from django.db.models import QuerySet

from framework.apps import BaseApp


class ProcessesConfig(BaseApp, AppConfig):
    """Configuration of the processes app.

    Attributes:
        name: Name of the app in the Django app registry.
        recreate_data: The default processes are reloaded on every migration, so a
          deployment gets the processes that each Rekono version defines.
    """

    name = "processes"
    recreate_data = True

    def load_fixtures(self, **kwargs: Any) -> None:
        """Load the process fixtures and remove the steps that can't run anymore.

        Deprecated configurations are preserved for historical executions, but a step
        referencing one can never run again, so it is removed to avoid leaving dead
        entries in process definitions. This runs after the tools fixtures have
        flagged the deprecated configurations, and after the process steps have been
        recreated.

        Args:
            **kwargs: Arguments sent by the post_migrate signal.
        """
        from processes.models import Step

        super().load_fixtures(**kwargs)
        Step.objects.filter(configuration__deprecated=True).delete()

    def _select_data_to_restore_relationships(self, model: Any) -> QuerySet:
        """Select the default processes, to keep the tasks that reference them.

        Args:
            model: The process model, which is about to be cleared.

        Returns:
            The processes without owner, with their tasks prefetched.
        """
        return model.objects.filter(owner__isnull=True).prefetch_related("tasks")

    def _select_data_to_recreate(self, model: Any) -> QuerySet:
        """Select the processes created by the users, with their tasks and steps.

        Args:
            model: The process model, which is about to be cleared.

        Returns:
            The processes with an owner, with their tasks and steps prefetched.
        """
        return model.objects.filter(owner__isnull=False).prefetch_related("tasks", "steps")

    def _get_current_entity_from_removed_entity(self, model: Any, removed: Any) -> Any:
        """Find the new default process with the same name as a removed one.

        The processes are matched by name because the fixtures may assign them a
        different identifier than the one they had.

        Args:
            model: The process model, where the replacement is searched.
            removed: Default process deleted before the reload.

        Returns:
            The new default process, or None if the fixtures no longer define one
            with that name, so the relationship can't be restored.
        """
        return model.objects.filter(name=removed.name).first()

    def _enable_relationship(self, entity: Any, relationship: str, queryset: QuerySet) -> None:
        """Assign the related objects to a process, recreating its steps.

        The steps can't be reassigned like the rest of the relationships, since they
        were deleted together with the process that owned them.

        Args:
            entity: Process that the related objects are assigned to.
            relationship: Name of the relationship to assign.
            queryset: Related objects to assign to it.
        """
        if relationship == "steps":
            for step in queryset:
                step.process = entity
                self._recreate_entity(step)
        else:
            super()._enable_relationship(entity, relationship, queryset)

    def _get_models(self) -> list[Any]:
        """Get the process model, whose data comes from the fixtures.

        Returns:
            The process model, imported inside the method because the models
            don't exist yet the first time that the migrations run.
        """
        from processes.models import Process

        return [Process]
