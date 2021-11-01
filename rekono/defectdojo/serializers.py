from defectdojo.api import engagements
from django.core.exceptions import ValidationError
from rest_framework import serializers


class EngagementSerializer(serializers.Serializer):
    engagement_id = serializers.IntegerField(required=False)
    engagement_name = serializers.CharField(max_length=100, required=False)
    engagement_description = serializers.CharField(max_length=300, required=False)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if 'engagement_id' in attrs:
            _, eng_id = engagements.check_engagement(attrs.get('engagement_id'))
            if not eng_id:
                raise ValidationError(
                    {'engagement_id': f'Engagement {attrs.get("engagement_id")} not found'}
                )
        elif not (
            'engagement_name' in attrs
            and attrs.get('engagement_name')
            and 'engagement_description' in attrs
            and attrs.get('engagement_description')
        ):
            raise ValidationError({
                'engagement_id': 'This field is required if engagement_name and engagement_description are not specified',  # noqa: E501
                'engagement_name': 'This field is required if engagement_id is not specified',
                'engagement_description': 'This field is required if engagement_id is not specified'
            })
        return attrs
