from rest_framework import serializers
from users.models import User
from authorization.groups.roles import Role
from django.contrib.sites.shortcuts import get_current_site


class InviteUserSerializer(serializers.Serializer):
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


class CreateUserSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150, required=True)
    first_name = serializers.CharField(max_length=150, required=True)
    last_name = serializers.CharField(max_length=150, required=True)
    password = serializers.CharField(max_length=150, required=True)
    otp = serializers.CharField(max_length=200, required=True)
    
    def create(self, validated_data):
        pk = self.context.get('pk', None)
        user = User.objects.get(pk=pk, is_active=False, otp=validated_data.get('otp'))
        user.username = validated_data.get('username')
        user.first_name = validated_data.get('first_name')
        user.last_name = validated_data.get('last_name')
        user.set_password(validated_data.get('password'))
        user.is_active = True
        user.otp = None
        user.save()
        return user
