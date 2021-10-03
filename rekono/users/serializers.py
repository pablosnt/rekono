from django.contrib.auth.models import Group
from rest_framework import serializers
from rest_framework.exceptions import ParseError
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


class ChangeUserRoleSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=Role.choices, required=True)

    def update(self, instance, validated_data):
        role = Role(validated_data.get('role'))
        group = Group.objects.get(name=role.name.capitalize())
        instance.groups.clear()
        instance.groups.set([group])
        instance.save()
        return instance


class UserSerializer(serializers.ModelSerializer):
    notification_preference = serializers.CharField(source='get_notification_preference_display')

    class Meta:
        model = User
        fields = (
            'id', 'username', 'first_name', 'last_name', 'email', 'is_active',
            'date_joined', 'last_login', 'groups', 'notification_preference',
            'telegram_token', 'binaryedge_apikey', 'bing_apikey', 'censys_apikey',
            'github_apikey', 'hunter_apikey', 'intelx_apikey', 'pentestTools_apikey',
            'projectDiscovery_apikey', 'rocketreach_apikey', 'securityTrails_apikey',
            'shodan_apikey', 'spyse_apikey', 'zoomeye_apikey'
        )
        read_only_fields = ('email', 'is_active', 'date_joined', 'last_login', 'groups')
        extra_kwargs = {
            'telegram_token': {'write_only': True},
            'binaryedge_apikey': {'write_only': True},
            'bing_apikey': {'write_only': True},
            'censys_apikey': {'write_only': True},
            'github_apikey': {'write_only': True},
            'hunter_apikey': {'write_only': True},
            'intelx_apikey': {'write_only': True},
            'pentestTools_apikey': {'write_only': True},
            'projectDiscovery_apikey': {'write_only': True},
            'rocketreach_apikey': {'write_only': True},
            'securityTrails_apikey': {'write_only': True},
            'shodan_apikey': {'write_only': True},
            'spyse_apikey': {'write_only': True},
            'zoomeye_apikey': {'write_only': True}
        }

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if 'get_notification_preference_display' in attrs:
            notification_preference = attrs.get('get_notification_preference_display')
            try:
                notification = User.Notification(int(notification_preference))
                attrs['notification_preference'] = notification.value
                attrs['get_notification_preference_display'] = notification.name.capitalize()
            except ValueError:
                raise ParseError(
                    f'Invalid {notification_preference} choice for notification_preference field'
                )
        return attrs
