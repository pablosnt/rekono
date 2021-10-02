from rest_framework import serializers
from users.models import User
from authorization.groups.roles import Role
from django.contrib.sites.shortcuts import get_current_site


class CreateUserSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    role = serializers.ChoiceField(choices=Role.choices, required=True)

    def create(self, validated_data):
        request = self.context.get('request', None)
        user = User.objects.create_user(
            validated_data.get('email'),
            Role(validated_data.get('role')),
            get_current_site(request).domain
        )
        return user
