"""Base Django app configuration that loads the fixtures of each Rekono app.

The default data of Rekono (tools, configurations, processes, wordlists, and
permissions) is shipped as fixtures that are loaded after every migration, so the
apps only have to declare which of their data is user-created and must survive that
reload.
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
    """Base app configuration that loads the app fixtures after the migrations.

    Apps whose default data changes between Rekono versions enable recreate_data,
    and override the selection hooks to keep the entities that the users created on
    the same models, since the whole model is deleted before the fixtures are
    loaded again.

    Attributes:
        skip_fixtures_if_model_exists: Load the fixtures only once, since any
          existing data means that they were already applied.
        recreate_data: Delete the data of the app models before loading the
          fixtures, so removed default entities disappear and updated ones are
          refreshed. Requires the selection hooks to be overridden if the users can
          create their own entities on those models.
    """

    skip_fixtures_if_model_exists = False
    recreate_data = False

    @cached_property
    def fixtures_path(self) -> Path:
        """The fixtures directory of the app that defines this configuration."""
        # nosemgrep: python.lang.security.audit.non-literal-import.non-literal-import
        module = importlib.import_module(self.__module__)
        return Path(module.__file__).resolve().parent / "fixtures"

    def ready(self) -> None:
        """Schedule the fixtures of the app to be loaded after each migration."""
        if self.fixtures_path and self.fixtures_path.is_dir():
            post_migrate.connect(self.load_fixtures, sender=self)

    def load_fixtures(self, **kwargs: Any) -> None:
        """Load all the fixture files of the app, keeping the user-created data.

        The entities selected by the hooks are read before the models are cleared,
        recreated after the fixtures are loaded, and finally reconnected to the new
        default entities that replaced the ones they referenced.

        Args:
            **kwargs: Arguments sent by the post_migrate signal.
        """
        if self.fixtures_path and self.fixtures_path.is_dir():
            entities_to_recreate = []
            entities_to_restore_relationships = []
            for model in self._get_models():
                if model.objects.exists():
                    if self.skip_fixtures_if_model_exists:
                        # Abort loading entirely, not just for this model, since any existing
                        # data means the fixtures were already applied
                        return  # pragma: no cover
                    entities_to_recreate.extend(list(self._select_data_to_recreate(model)))
                    entities_to_restore_relationships.extend(list(self._select_data_to_restore_relationships(model)))
                if self.recreate_data:
                    model.objects.all().delete()
            management.call_command(
                loaddata.Command(),
                *(self.fixtures_path / fixture for fixture in sorted(self.fixtures_path.rglob("*.json"))),
            )
            self._recreate(entities_to_recreate)
            for item in entities_to_restore_relationships:
                model = item.__class__
                entity = self._get_current_entity_from_removed_entity(model, item)
                if entity:
                    # The relationships were prefetched by the selection hook, so they are read
                    # from the removed entity even after its rows are gone from the database
                    for relationship, queryset in item.__dict__.get("_prefetched_objects_cache", {}).items():
                        self._enable_relationship(entity, relationship, queryset)

    def _select_data_to_restore_relationships(self, model: Any) -> QuerySet:
        """Select the entities whose relationships must be restored after the reload.

        Overridden by the apps that keep entities pointing to default data that the
        fixtures recreate with different identifiers. The relationships to restore
        must be prefetched by the returned queryset.

        Args:
            model: One of the app models that is about to be cleared.

        Returns:
            No entities, unless the app overrides this hook.
        """
        return model.objects.none()

    def _select_data_to_recreate(self, model: Any) -> QuerySet:
        """Select the entities that must be created again after the reload.

        Overridden by the apps whose models mix default data with entities created
        by the users, since only the latter would be lost.

        Args:
            model: One of the app models that is about to be cleared.

        Returns:
            No entities, unless the app overrides this hook.
        """
        return model.objects.none()

    def _recreate(self, data: list[Any]) -> None:
        """Create again all the entities that were removed before the reload.

        Args:
            data: Entities read from the selection hooks before the models were
              cleared, so they are no longer stored in the database.
        """
        for entity in data:
            self._recreate_entity(entity)

    def _recreate_entity(self, entity: Any) -> Any:
        """Create a new entity with the values and relationships of the given one.

        Args:
            entity: Removed entity whose values and prefetched relationships are
              copied into the new one.

        Returns:
            The new entity, which gets a new identifier since the original one may
            already be taken by the fixtures.
        """
        model = entity.__class__
        data = entity.__dict__
        new_entity = model.objects.create(
            **{
                field: value
                for field, value in data.items()
                if field not in ["id", "_state", "_prefetched_objects_cache"]
            }
        )
        for relationship, queryset in data.get("_prefetched_objects_cache", {}).items():
            self._enable_relationship(new_entity, relationship, queryset)
        return new_entity

    def _get_current_entity_from_removed_entity(self, model: Any, removed: Any) -> Any:
        """Find the entity created by the fixtures that replaces a removed one.

        Overridden by the apps that restore relationships, to define how a removed
        entity is matched against the new one, usually by a unique field.

        Args:
            model: Model where the replacement entity must be searched.
            removed: Entity deleted before the reload, whose values are the only
              way to identify its replacement.

        Returns:
            None, unless the app overrides this hook.
        """
        return None

    def _enable_relationship(self, entity: Any, relationship: str, queryset: QuerySet) -> None:
        """Assign the given related objects to one relationship of the entity.

        Args:
            entity: Entity whose relationship is set.
            relationship: Name of the many-to-many field to assign.
            queryset: Related objects to assign to that field.
        """
        getattr(entity, relationship).set(queryset)

    def _get_models(self) -> list[Any]:
        """Get the app models whose data is managed by the fixtures.

        Returns:
            No models, unless the app overrides this hook.
        """
        # Models can't be defined in a variable because the first time that the migrate command is executed,
        # models don't exist yet. They only can be imported from a post_migrate signal
        return []  # pragma: no cover
