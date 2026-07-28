"""Django REST framework serializers for target denylist models.

Provides serialization for target denylist records with proper field
configuration and read-only restrictions for administrative controls.
"""

from rest_framework.serializers import ModelSerializer

from target_denylist.models import TargetDenylist


class TargetDenylistSerializer(ModelSerializer):
    """Serializer for TargetDenylist model.

    Handles serialization of target denylist entries. The default and blocked
    fields are read-only via the API: default marks system-provided entries
    and blocked is a counter maintained internally by the target validator.
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
