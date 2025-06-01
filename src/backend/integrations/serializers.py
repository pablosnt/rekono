from integrations.models import Integration
from rest_framework.serializers import ModelSerializer


class IntegrationSerializer(ModelSerializer):
    class Meta:
        model = Integration
        fields = ("id", "name", "description", "enabled", "reference", "icon")
        read_only_fields = ("id", "name", "description", "reference", "icon")
