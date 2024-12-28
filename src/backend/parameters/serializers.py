from typing import Any

from parameters.models import InputTechnology, InputVulnerability
from rest_framework.serializers import ModelSerializer


class InputParameter(ModelSerializer):

    def save(self, **kwargs: Any) -> InputTechnology | InputVulnerability:
        search = self.Meta.model.filter(
            **{f: kwargs.get(f) for f in self.Meta.fields if f.lower() != "id"}
        )
        if search.exists():
            return search.first()
        return super().save(**kwargs)


class InputTechnologySerializer(InputParameter):
    """Serializer to manage input technologies via API."""

    class Meta:
        model = InputTechnology
        fields = ("id", "name", "version")


class InputVulnerabilitySerializer(InputParameter):
    """Serializer to manage input vulnerabilities via API."""

    class Meta:
        model = InputVulnerability
        fields = ("id", "cve")
