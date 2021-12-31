from rest_framework import serializers
from targets.models import Target, TargetEndpoint, TargetPort


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
