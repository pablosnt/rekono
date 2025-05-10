from datetime import date, datetime, timedelta
from typing import Any

from django.db.models import Count, QuerySet
from django.db.models.functions import TruncDate
from executions.models import Execution
from framework.models import BaseModel
from projects.models import Project
from rest_framework.serializers import PrimaryKeyRelatedField, Serializer
from targets.models import Target


class StatsSerializer(Serializer):
    project = PrimaryKeyRelatedField(many=False, write_only=True, required=False, queryset=Project.objects.all())
    target = PrimaryKeyRelatedField(many=False, write_only=True, required=False, queryset=Target.objects.all())
    model = BaseModel
    min_date = datetime.now() - timedelta(days=24 * 30)
    top = 5

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        if attrs.get("target"):
            attrs["project"] = None
        return super().validate(attrs)

    def _get_model(self, model: type[BaseModel] | None = None) -> type[BaseModel]:
        return model or self.model

    def _get_queryset(self, model: type[BaseModel] | None = None) -> QuerySet:
        db_model = self._get_model(model)
        project_field = db_model.get_project_field()
        filters = {
            (f"{project_field}__members__id" if project_field else "members__id"): self.context.get("request").user.id
        }
        if self.validated_data.get("target"):
            filters[project_field.split("__project")[0]] = self.validated_data.get("target")
        elif self.validated_data.get("project"):
            filters[project_field] = self.validated_data.get("project")
        return db_model.objects.filter(**filters)

    def _serialize(self, serializer_class: Any, queryset: QuerySet, many: bool = True) -> Any:
        return serializer_class(queryset, many=many, context=self.context).data

    def _get_serialized_evolution(self, serializer_class: Any, model: type[BaseModel] | None = None) -> Any:
        return self._serialize(serializer_class, self._get_evolution(model))

    def _get_evolution(self, model: type[BaseModel] | None = None) -> list[dict[str, Any]]:
        db_model = self._get_model(model)
        return [
            self._get_date_evolution(date, self._get_date_count(date, db_model))
            for date in self._get_queryset(Execution)
            .exclude(start=None)
            .filter(start__gte=self.min_date)
            .annotate(count=Count(db_model.__name__.lower()))
            .filter(count__gt=0)
            .annotate(date=TruncDate("start"))
            .values_list("date", flat=True)
            .distinct()
        ]

    def _get_date_evolution(self, date: date, count: Any) -> Any:
        return {"date": date, "count": count}

    def _get_date_count(self, date: date, model: type[BaseModel]) -> Any:
        return 0
