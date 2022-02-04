from typing import Any, Dict

from defectdojo.api import DefectDojo
from django.core.exceptions import ValidationError
from rest_framework import serializers
from security.input_validation import validate_name, validate_text


class EngagementSerializer(serializers.Serializer):
    '''Serializer to allow the import of findings and executions in Defect-Dojo using an engagement.'''

    id = serializers.IntegerField(required=False)                               # Using an existing engagement
    name = serializers.CharField(max_length=100, required=False)                # Name of the new engagement
    description = serializers.CharField(max_length=300, required=False)         # Description of the new engagement

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
        if 'id' in attrs:                                                       # Import using an existing engagement
            success, _ = DefectDojo().get_engagement(attrs['id'])               # Check if the engagement Id exists
            if not success:
                raise ValidationError({'id': f'Engagement {attrs.get("id")} not found'})
        elif not (                                                              # Id or (name and description) required
            'name' in attrs and attrs.get('name') and
            'description' in attrs and attrs.get('description')
        ):
            raise ValidationError({
                'id': 'This field is required if "name" and "description" are not provided',
                'name': 'This field is required if "id" is not specified',
                'description': 'This field is required if "id" is not specified'
            })
        else:
            try:
                validate_name(attrs['name'])                                    # Check name value
            except ValidationError as ex:
                raise ValidationError({'name': str(ex)})
            try:
                validate_text(attrs['description'])                             # Check description value
            except ValidationError as ex:
                raise ValidationError({'description': str(ex)})
        return attrs
