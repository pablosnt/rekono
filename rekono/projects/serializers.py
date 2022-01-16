from typing import Any, Dict

from api.serializers import RekonoTagSerializerField
from defectdojo.api import DefectDojo
from django.db import transaction
from projects.models import Project
from rest_framework import serializers
from taggit.serializers import TaggitSerializer
from targets.serializers import TargetSerializer
from users.models import User
from users.serializers import SimplyUserSerializer


class ProjectSerializer(TaggitSerializer, serializers.ModelSerializer):
    '''Serializer to manage projects via API.'''

    targets = TargetSerializer(read_only=True, many=True)                       # Targets details for reaad operations
    owner = SimplyUserSerializer(many=False, read_only=True)                    # Owner details for read operations
    tags = RekonoTagSerializerField()                                           # Tags

    class Meta:
        '''Serializer metadata.'''

        model = Project
        # Project fields exposed via API
        fields = ('id', 'name', 'description', 'defectdojo_product_id', 'owner', 'targets', 'members', 'tags')
        read_only_fields = ('owner', 'members')                                 # Read only fields

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        '''Validate the provided data before use it.

        Args:
            attrs (Dict[str, Any]): Provided data

        Raises:
            ValidationError: Raised if provided data is invalid

        Returns:
            Dict[str, Any]: Data after validation process
        '''
        attrs = super().validate(attrs)
        if attrs.get('defectdojo_product_id'):
            # Check if product Id exists in Defect-Dojo
            success, _ = DefectDojo().get_product(attrs['defectdojo_product_id'])
        if attrs.get('defectdojo_product_id') and not success:
            # Product Id not found in Defect-Dojo
            raise serializers.ValidationError(
                {'defectdojo_product_id': f'Product ID {attrs.get("defectdojo_product_id")} not found in Defect-Dojo'}
            )
        return attrs

    @transaction.atomic()
    def create(self, validated_data: Dict[str, Any]) -> Project:
        '''Create instance from validated data.

        Args:
            validated_data (Dict[str, Any]): Validated data

        Returns:
            Project: Created instance
        '''
        project = super().create(validated_data)                                # Create project
        project.members.add(validated_data.get('owner'))                        # Add project owner also in member list
        project.save(update_fields=['members'])
        return project


class ProjectMemberSerializer(serializers.Serializer):
    '''Serializer to add new member to a project via API.'''

    user = serializers.IntegerField(required=True)                              # User Id to add to the project members

    @transaction.atomic()
    def update(self, instance: Project, validated_data: Dict[str, Any]) -> Project:
        '''Update instance from validated data.

        Args:
            instance (Project): Instance to update
            validated_data (Dict[str, Any]): Validated data

        Returns:
            Project: Updated instance
        '''
        user = User.objects.get(pk=validated_data.get('user'), is_active=True)  # Get active user from user Id
        instance.members.add(user)                                              # Add user as project member
        instance.save(update_fields=['members'])
        return instance
