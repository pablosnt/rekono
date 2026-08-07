"""Base serializer of the input parameters."""

from typing import Any

from rest_framework.serializers import ModelSerializer

from parameters.models import InputTechnology, InputVulnerability


class InputParameterSerializer(ModelSerializer):
    """Base serializer of an input parameter, which is never duplicated."""

    def create(self, validated_data: dict[str, Any]) -> InputTechnology | InputVulnerability:
        """Create a new parameter with the given data.

        Args:
            validated_data: Parameter fields, already validated.

        Returns:
            The existing parameter with the same data, if there is one, since the
            parameters are shared by all the tasks that use them.
        """
        # The id field is excluded because it is auto-generated and never present in validated_data,
        # so comparing on it would prevent any duplicate from matching
        search = self.__class__.Meta.model.objects.filter(
            **{f: validated_data.get(f) for f in self.Meta.fields if f.lower() != "id"}
        )
        if search.exists():
            return search.first()
        return super().create(validated_data)
