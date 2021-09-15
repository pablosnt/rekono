from rest_framework import serializers
from projects.models import Project, Target, TargetPort
from django.db import transaction
from projects import utils


class ProjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = Project
        fields = ('id', 'name', 'description', 'owner', 'targets')
        read_only_fields = ('owner', 'targets')


class TargetPortSerializer(serializers.ModelSerializer):

    class Meta:
        model = TargetPort
        fields = ('port',)


class TargetSerializer(serializers.ModelSerializer):
    target_ports = TargetPortSerializer(read_only=False, many=True, required=False)
    type = serializers.CharField(source='get_type_display', read_only=True)

    class Meta:
        model = Target
        fields = (
            'id', 'project', 'target', 'type', 'target_ports', 'requests'
        )
        read_only_fields = ('type', 'requests')

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
