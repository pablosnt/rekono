"""Custom field implementations for tools serialization.

Provides specialized field classes for tools-specific data types with
custom serialization logic and representation formatting.
"""

from framework.fields import IntegerChoicesField


class StageField(IntegerChoicesField):
    """Custom field for Stage enum with specialized representation formatting.

    Extends IntegerChoicesField to provide custom string representation
    for Stage enum values, with special formatting for OSINT stage.
    """

    def to_representation(self, value: int) -> str:
        """Convert stage value to string representation.

        Applies custom formatting rules, specifically converting OSINT
        stage (value=1) to uppercase for consistent display.

        Args:
            value (int): The stage enum integer value

        Returns:
            str: Formatted string representation of the stage
        """
        representation = super().to_representation(value)
        if value == 1:
            representation = representation.upper()
        return representation
