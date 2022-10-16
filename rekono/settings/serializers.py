from typing import Any

from rest_framework import serializers

from settings.models import Setting


class SettingSerializer(serializers.ModelSerializer):

    value = serializers.SerializerMethodField(method_name='get_value')

    class Meta:
        model = Setting
        fields = ('id', 'field', 'value', 'protected')
        read_only_fields = ('field', 'protected')
    
    def get_value(self, instance: Any) -> str:
        if instance.protected and instance.value:
            return '*' * 5
        return instance.value
