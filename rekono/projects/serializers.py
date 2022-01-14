from api.serializers import RekonoTagSerializerField
from defectdojo.api import DefectDojo
from django.db import transaction
from projects.models import Project
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from taggit.serializers import TaggitSerializer
from targets.serializers import TargetSerializer
from users.models import User
from users.serializers import SimplyUserSerializer


class ProjectSerializer(TaggitSerializer, serializers.ModelSerializer):
    targets = TargetSerializer(read_only=True, many=True)
    owner = SerializerMethodField(method_name='get_owner', read_only=True, required=False)
    tags = RekonoTagSerializerField()

    class Meta:
        model = Project
        fields = (
            'id', 'name', 'description', 'defectdojo_product_id', 'owner',
            'targets', 'members', 'tags'
        )
        read_only_fields = ('owner', 'members')

    def get_owner(self, instance: Project) -> SimplyUserSerializer:
        return SimplyUserSerializer(instance.owner).data

    def validate(self, attrs):
        attrs = super().validate(attrs)
        success, _ = DefectDojo().get_product(attrs.get('defectdojo_product_id'))
        if (
            attrs.get('defectdojo_product_id')
            and not success
        ):
            raise serializers.ValidationError(
                {
                    'defectdojo_product_id': f'Product ID {attrs.get("defectdojo_product_id")} not found in Defect-Dojo'    # noqa: E501
                }
            )
        return attrs

    @transaction.atomic()
    def create(self, validated_data):
        project = super().create(validated_data)
        project.members.add(validated_data.get('owner'))
        project.save()
        return project


class ProjectMemberSerializer(serializers.Serializer):
    user = serializers.IntegerField(required=True)

    @transaction.atomic()
    def update(self, instance, validated_data):
        user = User.objects.get(pk=validated_data.get('user'), is_active=True)
        instance.members.add(user)
        instance.save()
        return instance
