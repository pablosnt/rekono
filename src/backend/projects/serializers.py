import logging
from typing import Any, Dict

from api.fields import RekonoTagField
from defectdojo.api import DefectDojo
from defectdojo.exceptions import DefectDojoException
from django.db import transaction
from django.forms import ValidationError
from rest_framework import serializers
from security.input_validation import validate_name, validate_text
from taggit.serializers import TaggitSerializer
from targets.serializers import TargetSerializer
from users.models import User
from users.serializers import SimplyUserSerializer

from projects.models import Project

logger = logging.getLogger()                                                    # Rekono logger


class ProjectSerializer(TaggitSerializer, serializers.ModelSerializer):
    '''Serializer to manage projects via API.'''

    targets = TargetSerializer(read_only=True, many=True)                       # Targets details for reaad operations
    owner = SimplyUserSerializer(many=False, read_only=True)                    # Owner details for read operations
    tags = RekonoTagField()                                                     # Tags

    class Meta:
        '''Serializer metadata.'''

        model = Project
        fields = (                                                              # Project fields exposed via API
            'id', 'name', 'description', 'defectdojo_product_id', 'defectdojo_engagement_id',
            'defectdojo_engagement_by_target', 'defectdojo_synchronization', 'owner', 'targets', 'members', 'tags'
        )
        read_only_fields = (                                                    # Read only fields
            'defectdojo_product_id', 'defectdojo_engagement_id', 'defectdojo_engagement_by_target',
            'defectdojo_synchronization', 'owner', 'targets', 'members'
        )

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
        return instance


class DefectDojoIntegrationSerializer(serializers.Serializer):
    '''Serializer to configure Defect-Dojo integration for one project via API.'''

    product_id = serializers.IntegerField(required=False)                       # Using an existing product
    engagement_id = serializers.IntegerField(required=False)                    # Using an existing engagement
    engagement_name = serializers.CharField(max_length=100, required=False)     # Name of the new engagement
    engagement_description = serializers.CharField(max_length=300, required=False)  # Description of the new engagement

    def __init__(self, instance: Any = None, data: Any = ..., **kwargs):
        '''Initialize the serializer.

        Args:
            instance (Any, optional): Model instance. Defaults to None.
            data (Any, optional): Data provided for the operations. Defaults to ....
        '''
        super().__init__(instance, data, **kwargs)
        self.dd_client = DefectDojo()

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        '''Validate the provided data before use it.

        Args:
            attrs (Dict[str, Any]): Provided data

        Raises:
            ValidationError: Raised if provided data is invalid

        Returns:
            Dict[str, Any]: Data after validation process
        '''
        if not self.dd_client.is_available():
            raise serializers.ValidationError({'defect-dojo': ['Integration with Defect-Dojo is not available']})
        attrs = super().validate(attrs)
        if attrs.get('engagement_id'):                                          # If engagement Id provided
            success, body = self.dd_client.get_engagement(attrs['engagement_id'])   # Check engagement Id
            if success:
                attrs['product_id'] = body.get('product')                       # Save related product Id
            else:
                raise serializers.ValidationError({'engagement_id': 'Engagement not found in Defect-Dojo'})
        elif attrs.get('product_id'):                                           # If not engagement Id but product Id
            success, body = self.dd_client.get_product(attrs['product_id'])     # Check product Id
            if not success:
                raise serializers.ValidationError({'product_id': 'Product not found in Defect-Dojo'})
        if (                                                                    # If new engagement is needed
            not attrs.get('engagement_id') and
            attrs.get('engagement_name') and
            attrs.get('engagement_description')
        ):
            for field, validator in [
                ('engagement_name', validate_name),
                ('engagement_description', validate_text)
            ]:
                try:
                    validator(attrs[field])                                     # Validate name and description fields
                except ValidationError as ex:
                    raise serializers.ValidationError({field: str(ex)})
        return attrs

    def update(self, instance: Project, validated_data: Dict[str, Any]) -> Project:
        '''Update instance from validated data.

        Args:
            instance (Project): Instance to update
            validated_data (Dict[str, Any]): Validated data

        Raises:
            DefectDojoException: Raised if Defect-Dojo entities are not found or can't be created

        Returns:
            Project: Updated instance
        '''
        if not validated_data.get('product_id'):                                # DD product creation required
            product_type = 0
            success, body = self.dd_client.get_rekono_product_type()            # Get Rekono product type in Defect-Dojo
            if success and len(body.get('results') or []) > 0:
                product_type = body['results'][0].get('id')                     # Rekono product type found
            else:
                success, body = self.dd_client.create_rekono_product_type()     # Create Rekono product type in DD
                if not success:
                    logger.error("[Defect-Dojo] Rekono product type can't be created")
                    raise DefectDojoException({'product_type': ["Rekono product type can't be created in Defect-Dojo"]})
                logger.info('[Defect-Dojo] Rekono product type has been created')
                product_type = body['id']
            # Create product related to the project
            success, body = self.dd_client.create_product(product_type, instance)
            if not success:
                logger.error(f"[Defect-Dojo] Product related to project {instance.id} can't be created")
                raise DefectDojoException(
                    {'product': [f"Defect-Dojo product related to project {instance.id} can't be created"]}
                )
            logger.info(f'[Defect-Dojo] New product {body["id"]} related to project {instance.id} has been created')
            validated_data['product_id'] = body.get('id')
        instance.defectdojo_product_id = validated_data.get('product_id')
        instance.save(update_fields=['defectdojo_product_id'])
        if (                                                                    # DD engagement creation required
            not validated_data.get('engagement_id') and
            validated_data.get('engagement_name') and
            validated_data.get('engagement_description')
        ):
            success, body = self.dd_client.create_engagement(                          # Create engagement
                validated_data['product_id'],
                validated_data['engagement_name'],
                validated_data['engagement_description']
            )
            if not success:
                logger.error(f"[Defect-Dojo] Engagement related to project {instance.id} can't be created")
                raise DefectDojoException(
                    {'engagement': [f"Defect-Dojo engagement related to project {instance.id} can't be created"]}
                )
            logger.info(f'[Defect-Dojo] New engagement {body["id"]} has been created')
            validated_data['engagement_id'] = body.get('id')
        instance.defectdojo_engagement_id = validated_data.get('engagement_id')
        # If no engagement provided, one engagement for each target will be created
        instance.defectdojo_engagement_by_target = validated_data.get('engagement_id') is None
        instance.save(update_fields=['defectdojo_engagement_id', 'defectdojo_engagement_by_target'])
        return instance


class DefectDojoSyncSerializer(serializers.Serializer):
    '''Serializer to enable and disable the Defect-Dojo synchronization for one project via API.'''

    synchronization = serializers.BooleanField(required=True)                   # Enable/Disable Defect-Dojo sync

    def update(self, instance: Project, validated_data: Dict[str, Any]) -> Project:
        '''Update instance from validated data.

        Args:
            instance (Project): Instance to update
            validated_data (Dict[str, Any]): Validated data

        Returns:
            Project: Updated instance
        '''
        if not instance.defectdojo_product_id:
            raise DefectDojoException(
                {'defectdojo_product_id': [f'Defect-Dojo integration is not configured for project {instance.id}']}
            )
        instance.defectdojo_synchronization = validated_data.get('synchronization')
        instance.save(update_fields=['defectdojo_synchronization'])
        return instance
