from django.db import transaction
from rest_framework import serializers
from targets import utils
from targets.models import Target, TargetPort


class TargetPortSerializer(serializers.ModelSerializer):

    class Meta:
        model = TargetPort
        fields = ('id', 'port')
        ordering = ['-id']


class TargetSerializer(serializers.ModelSerializer):
    target_ports = TargetPortSerializer(read_only=False, many=True, required=False)

    class Meta:
        model = Target
        fields = (
            'id', 'project', 'target', 'type', 'target_ports', 'tasks'
        )
        read_only_fields = ('type', 'tasks')
        ordering = ['-id']

    @transaction.atomic()
    def create(self, validated_data):
        target = Target.objects.create(
            project=validated_data.get('project'),
            target=validated_data.get('target'),
            type=utils.get_target_type(validated_data.get('target'))
        )
        if 'target_ports' in validated_data:
            target_ports_data = validated_data.pop('target_ports')
            for target_port in target_ports_data:
                target_port['target'] = target
                TargetPortSerializer().create(
                    validated_data=target_port
                )
        return target
