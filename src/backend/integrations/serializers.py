from rest_framework.serializers import ModelSerializer
from integrations.models import Integration


class IntegrationSerializer(ModelSerializer):
    class Meta:
        model = Integration
        fields = ("id", "name", "description", "enabled", "reference")
        read_only_fields = ("id", "name", "description", "reference")
