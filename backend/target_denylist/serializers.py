"""Django REST framework serializers for target denylist models.

Provides serialization for target denylist records with proper field
configuration and read-only restrictions for administrative controls.
"""

from rest_framework.serializers import ModelSerializer

from target_denylist.models import TargetDenylist


class TargetDenylistSerializer(ModelSerializer):
    """Serializer for TargetDenylist model.

    Handles serialization of target denylist entries with read-only protection
    for the default field to prevent unauthorized modification of system entries.
    """

    class Meta:
        """Meta configuration for TargetDenylistSerializer.

        Attributes:
            model (type): TargetDenylist model class.
            fields (tuple): Field names included in serialization.
            read_only_fields (tuple): Fields protected from modification.
        """

        model = TargetDenylist
        fields = ("id", "target", "default", "blocked")
        read_only_fields = ("default", "blocked")
