"""Django app configuration utilities for Rekono framework.

Provides base app class with automatic fixture loading capabilities
for Django applications in the Rekono platform.
"""

import importlib
from functools import cached_property
from pathlib import Path
from typing import Any

from django.core import management
from django.core.management.commands import loaddata
from django.db.models import QuerySet
from django.db.models.signals import post_migrate


class BaseApp:
    """Base Django application configuration with fixture loading capabilities.

    Provides automatic loading of fixture files after database migrations
    for consistent data initialization across Django applications.

    Attributes:
        skip_fixtures_if_model_exists (bool): Whether to skip loading if data exists.
        recreate_data (bool): Whether to recreate all model data during fixture loading.
            When True, preserves user-created entities while refreshing default data.
            Required when new default entities can be defined, old ones removed,
            and users can create custom entities on the same model.
    """

    skip_fixtures_if_model_exists = False
    recreate_data = False

    @cached_property
    def fixtures_path(self) -> Path:
        """Get the path to the application's fixtures directory.

        Dynamically determines the fixtures directory path based on the
        application module location, following Django conventions.

        Returns:
            Path: Absolute path to the fixtures directory for this application.
        """
        module = importlib.import_module(self.__module__)
        return Path(module.__file__).resolve().parent / "fixtures"

    def ready(self) -> None:
        """Configure the application after Django starts.

        Sets up post-migration signal to automatically load fixtures
        if the fixtures directory exists.
        """
        # Configure fixtures to be loaded after migration
        if self.fixtures_path and self.fixtures_path.is_dir():
            post_migrate.connect(self.load_fixtures, sender=self)

    def load_fixtures(self, **kwargs: Any) -> None:
        """Load fixture files into the database with data preservation support.

        Called automatically after migrations to populate the database with initial data.
        Supports preserving user-created entities and their relationships during
        fixture recreation when recreate_data is enabled.

        Args:
            **kwargs (Any): Signal arguments from post_migrate.
        """
        if self.fixtures_path and self.fixtures_path.is_dir():
            entities_to_recreate = []
            entities_to_restore_relationships = []
            # Phase 1: Collect data that needs to survive the recreation process
            for model in self._get_models():
                if model.objects.exists():
                    if self.skip_fixtures_if_model_exists:
                        return  # pragma: no cover
                    # Collect user-created entities that should be preserved
                    entities_to_recreate.extend(list(self._select_data_to_recreate(model)))
                    # Collect entities whose relationships need restoration
                    entities_to_restore_relationships.extend(list(self._select_data_to_restore_relationships(model)))
                # Phase 2: Clear existing data if recreation is enabled
                if self.recreate_data:
                    model.objects.all().delete()
            # Phase 3: Load fresh fixture data from JSON files
            management.call_command(
                loaddata.Command(),
                *(self.fixtures_path / fixture for fixture in sorted(self.fixtures_path.rglob("*.json"))),
            )
            # Phase 4: Recreate preserved user entities
            self._recreate(entities_to_recreate)
            # Phase 5: Restore relationships for entities that need them
            for item in entities_to_restore_relationships:
                model = item.__class__
                # Find the corresponding new entity for relationship restoration
                entity = self._get_current_entity_from_removed_entity(model, item)
                if entity:
                    # Restore all prefetched relationships from the original entity
                    for relationship, queryset in item.__dict__.get("_prefetched_objects_cache", {}).items():
                        self._enable_relationship(entity, relationship, queryset)

    def _select_data_to_restore_relationships(self, model: Any) -> QuerySet:
        """Select model instances whose relationships should be restored after recreation.

        This method identifies entities that should have their many-to-many and
        foreign key relationships preserved during the data recreation process.

        Args:
            model (Any): The Django model class to query.

        Returns:
            QuerySet: QuerySet of instances needing relationship restoration.
        """
        return model.objects.none()

    def _select_data_to_recreate(self, model: Any) -> QuerySet:
        """Select model instances that should be preserved during fixture recreation.

        This method identifies user-created or custom entities that should be
        saved before model data deletion and recreated after fixture loading.

        Args:
            model (Any): The Django model class to query.

        Returns:
            QuerySet: QuerySet of instances to preserve and recreate.
        """
        return model.objects.none()

    def _recreate(self, data: list[Any]) -> None:
        """Recreate a list of preserved entities after fixture loading.

        Iterates through the provided list of entities and recreates each one
        using the _recreate_entity method to restore their data and relationships.

        Args:
            data (list[Any]): List of model instances to recreate.
        """
        for entity in data:
            self._recreate_entity(entity)

    def _recreate_entity(self, entity: Any) -> Any:
        """Recreate a model instance with its data and relationships.

        Creates a new database record with the same field values as the original
        entity, excluding internal Django fields, and restores relationships.

        Args:
            entity (Any): The original model instance to recreate.

        Returns:
            Any: The newly created model instance with restored relationships.
        """
        model = entity.__class__
        data = entity.__dict__
        # Create new instance excluding Django internal fields
        new_entity = model.objects.create(
            **{
                field: value
                for field, value in data.items()
                if field not in ["id", "_state", "_prefetched_objects_cache"]
            }
        )
        # Restore relationships from prefetched cache
        for relationship, queryset in data.get("_prefetched_objects_cache", {}).items():
            self._enable_relationship(new_entity, relationship, queryset)
        return new_entity

    def _get_current_entity_from_removed_entity(self, model: Any, removed: Any) -> Any:
        """Find the current equivalent of a removed entity after fixture reload.

        This method attempts to locate the newly created entity that corresponds
        to a previously removed entity, typically by matching identifying fields.

        Args:
            model (Any): The Django model class to search in.
            removed (Any): The original entity that was removed.

        Returns:
            Any: The corresponding new entity instance, or None if not found.
        """
        return None

    def _enable_relationship(self, entity: Any, relationship: str, queryset: QuerySet) -> None:
        """Restore a relationship between an entity and related objects.

        Sets up many-to-many or foreign key relationships for the given entity
        using the provided queryset of related objects.

        Args:
            entity (Any): The model instance to set relationships for.
            relationship (str): The name of the relationship field.
            queryset (QuerySet): The related objects to associate.
        """
        getattr(entity, relationship).set(queryset)

    def _get_models(self) -> list[Any]:
        """Get model classes for existence checking.

        Returns:
            list[Any]: List of model classes to check for existing data.

        Note:
            This method should be overridden by subclasses to return
            the relevant model classes for the application.
        """
        # Models can't be defined in a variable because the first time that the migrate command is executed,
        # models don't exist yet. They only can be imported from a post_migrate signal
        return []  # pragma: no cover
