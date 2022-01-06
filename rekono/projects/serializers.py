from defectdojo.api import products
from django.db import transaction
from projects.models import Project
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from targets.serializers import TargetSerializer
from users.models import User
from users.serializers import SimplyUserSerializer


class ProjectSerializer(serializers.ModelSerializer):
    targets = TargetSerializer(read_only=True, many=True)
    owner = SerializerMethodField(method_name='get_owner', read_only=True, required=False)

    class Meta:
        model = Project
        fields = (
            'id', 'name', 'description', 'defectdojo_product_id', 'owner', 'targets', 'members'
        )
        read_only_fields = ('owner', 'members')
        extra_kwargs = {
            'defectdojo_product_id': {'required': False}
        }

    def get_owner(self, instance: Project) -> SimplyUserSerializer:
        return SimplyUserSerializer(instance.owner).data

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if (
            attrs.get('defectdojo_product_id')
            and not products.check_product_id(attrs.get('defectdojo_product_id'))
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
