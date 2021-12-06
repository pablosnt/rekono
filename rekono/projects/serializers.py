from defectdojo.api import products
from django.db import transaction
from projects.models import Project
from rest_framework import serializers
from targets.serializers import SimplyTargetSerializer
from users.models import User


class ProjectSerializer(serializers.ModelSerializer):
    targets = SimplyTargetSerializer(read_only=True, many=True)

    class Meta:
        model = Project
        fields = (
            'id', 'name', 'description', 'defectdojo_product_id', 'owner', 'targets', 'members'
        )
        read_only_fields = ('owner', 'members')

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
