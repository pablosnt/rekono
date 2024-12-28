from typing import Any

from parameters.models import InputTechnology, InputVulnerability
from rest_framework.serializers import ModelSerializer


class InputParameterSerializer(ModelSerializer):

    def create(
        self, validated_data: dict[str, Any]
    ) -> InputTechnology | InputVulnerability:
        search = self.__class__.Meta.model.objects.filter(
            **{f: validated_data.get(f) for f in self.Meta.fields if f.lower() != "id"}
        )
        if search.exists():
            return search.first()
        return super().create(validated_data)
