from typing import Any

from rest_framework import serializers

from settings.models import Setting


class SettingSerializer(serializers.ModelSerializer):

    value = serializers.SerializerMethodField(method_name='get_value')

    class Meta:
        model = Setting
        fields = ('id', 'field', 'value', 'private', 'modified_by')
        read_only_fields = ('field', 'private', 'modified_by')
    
    def get_value(self, instance: Any) -> str:
        if instance.private and instance.value:
            return '*' * len(instance.value)
        return instance.value

    def update(self, instance, validated_data):
        instance.validate()
        return super().update(instance, validated_data)
