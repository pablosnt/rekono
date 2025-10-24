"""Django application configuration for process management module.

Provides application configuration for the processes module with fixture
management and model registration for security testing workflow management.
"""

from typing import Any

from django.apps import AppConfig
from django.db.models import QuerySet

from framework.apps import BaseApp


class ProcessesConfig(BaseApp, AppConfig):
    """Django application configuration for the processes module.

    Configures the processes application with fixture management and
    model registration for security testing workflow components.

    Attributes:
        name (str): Application name for Django registration
        recreate_data (bool): Enable full data recreation during fixture loading
    """

    name = "processes"
    recreate_data = True

    def _select_data_to_restore_relationships(self, model: Any) -> QuerySet:
        """Select default processes that need relationship restoration.

        Identifies default processes (owner is None) that should have
        their task relationships restored after the recreation process.

        Args:
            model (Any): The Process model class.

        Returns:
            QuerySet: Default processes with prefetched task relationships.
        """
        return model.objects.filter(owner__isnull=True).prefetch_related("tasks")

    def _select_data_to_recreate(self, model: Any) -> QuerySet:
        """Select user-created processes to preserve during fixture recreation.

        Identifies custom processes created by users (owner is not None) that
        should be preserved with their tasks and steps during data recreation.

        Args:
            model (Any): The Process model class.

        Returns:
            QuerySet: User processes with prefetched tasks and steps.
        """
        return model.objects.filter(owner__isnull=False).prefetch_related("tasks", "steps")

    def _get_current_entity_from_removed_entity(self, model: Any, removed: Any) -> Any:
        """Find the current process that matches a removed process by name.

        Locates the newly created process instance that corresponds to a
        removed process by matching the name field. Note that after re-creation
        database IDs might change.

        Args:
            model (Any): The Process model class.
            removed (Any): The removed process instance.

        Returns:
            Any: The matching process instance, or None if not found.
        """
        return model.objects.filter(name=removed.name).first()

    def _enable_relationship(self, entity: Any, relationship: str, queryset: QuerySet) -> None:
        """Restore relationships for a process, with special handling for steps.

        Restores relationships between processes and related entities, with
        custom logic for step relationships that require recreation.

        Args:
            entity (Any): The process instance to restore relationships for.
            relationship (str): The name of the relationship field.
            queryset (QuerySet): The related objects to associate.
        """
        if relationship == "steps":
            # Steps need to be recreated with the new process reference
            for step in queryset:
                step.process = entity
                self._recreate_entity(step)
        else:
            super()._enable_relationship(entity, relationship, queryset)

    def _get_models(self) -> list[Any]:
        """Get the model classes for this application.

        Returns:
            list[Any]: List containing Process model class.
        """
        from processes.models import Process

        return [Process]
