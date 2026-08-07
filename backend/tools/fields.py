"""Serializer fields of the tool endpoints."""

from framework.fields import IntegerChoicesField


class StageField(IntegerChoicesField):
    """Stage of a configuration, serialized as its name."""

    def to_representation(self, value: int) -> str:
        """Get the name of the stage, with OSINT written as an acronym.

        Args:
            value: Stage value stored in the database.

        Returns:
            The capitalized stage name, uppercased for OSINT.
        """
        representation = super().to_representation(value)
        if value == 1:
            representation = representation.upper()
        return representation
