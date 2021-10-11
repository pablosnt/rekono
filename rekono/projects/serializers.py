from rest_framework import serializers
from projects.models import Project, Target, TargetPort
from django.db import transaction
from projects import utils
from users.models import User


class ProjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = Project
        fields = (
            'id', 'name', 'description', 'defectdojo_product_id', 'owner', 'targets', 'members'
        )
        read_only_fields = ('owner', 'targets', 'members')
        ordering = ['-id']

    def create(self, validated_data):
        project = super().create(validated_data)
        project.members.add(validated_data.get('owner'))
        project.save()
        return project


class ProjectMemberSerializer(serializers.Serializer):
    user = serializers.IntegerField(required=True)

    def update(self, instance, validated_data):
        user = User.objects.get(pk=validated_data.get('user'), is_active=True)
        instance.members.add(user)
        instance.save()
        return instance


class TargetPortSerializer(serializers.ModelSerializer):

    class Meta:
        model = TargetPort
        fields = ('id', 'port')
        ordering = ['-id']


class TargetSerializer(serializers.ModelSerializer):
    target_ports = TargetPortSerializer(read_only=False, many=True, required=False)
    type = serializers.CharField(source='get_type_display', read_only=True)

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
