from django.core.exceptions import ValidationError
from rest_framework import serializers
from targets.exceptions import InvalidTargetException
from targets.models import Target, TargetEndpoint, TargetPort
from targets.utils import get_target_type


class TargetEndpointSerializer(serializers.ModelSerializer):

    class Meta:
        model = TargetEndpoint
        fields = ('id', 'target_port', 'endpoint')


class TargetPortSerializer(serializers.ModelSerializer):
    target_endpoints = TargetEndpointSerializer(many=True, read_only=True, required=False)

    class Meta:
        model = TargetPort
        fields = ('id', 'target', 'port', 'target_endpoints')
        read_only_fields = ('target_endpoints',)


class TargetSerializer(serializers.ModelSerializer):
    target_ports = TargetPortSerializer(many=True, read_only=True, required=False)

    class Meta:
        model = Target
        fields = ('id', 'project', 'target', 'type', 'target_ports', 'tasks')
        read_only_fields = ('type', 'target_ports', 'tasks')
    
    def validate(self, attrs):
        attrs = super().validate(attrs)
        try:
            attrs['type'] = get_target_type(attrs.get('target'))
            return attrs
        except InvalidTargetException:
            raise ValidationError(
                {'target': f'Invalid target {attrs.get("target")} '}
            )


class SimplyTargetSerializer(serializers.ModelSerializer):

    class Meta:
        model = Target
        fields = ('id', 'project', 'target', 'type')
        read_only_fields = ('type',)
