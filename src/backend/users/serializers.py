import threading
from typing import Any

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import CharField, ChoiceField, EmailField, ModelSerializer, Serializer, URLField

from platforms.mail.notifications import SMTP
from platforms.telegram_app.notifications import Telegram
from security.authentication.serializers import MfaSerializer
from security.authorization.roles import Role
from users.models import User


class UserSerializer(ModelSerializer):
    role = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "is_active",
            "date_joined",
            "last_login",
            "role",
        )

    def get_role(self, instance: User) -> str:
        role = instance.groups.first()
        return role.name if role else Role.READER.value


class SimpleUserSerializer(UserSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "role")


class InviteUserSerializer(ModelSerializer):
    role = ChoiceField(choices=Role.choices, required=True, write_only=True)

    class Meta:
        model = User
        fields = ("email", "role")

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        attrs = super().validate(attrs)
        if not SMTP().is_available():
            raise ValidationError("SMTP client is not available to send the invitation", code="smtp")
        return attrs

    def create(self, validated_data: dict[str, Any]) -> User:
        return User.objects.invite_user(validated_data["email"], Role(validated_data["role"]))


class UpdateRoleSerializer(Serializer):
    role = ChoiceField(choices=Role.choices, required=True, write_only=True)

    def update(self, instance: User, validated_data: dict[str, Any]) -> User:
        return User.objects.assign_role(instance, Role(validated_data["role"]))


class ProfileSerializer(UserSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "date_joined",
            "last_login",
            "mfa",
            "role",
            "telegram_chat",
            "notification_scope",
            "email_notifications",
            "telegram_notifications",
        )
        read_only_fields = ("username", "email", "date_joined", "last_login", "mfa", "role", "telegram_chat")


class PasswordSerializer(UserSerializer):
    class Meta:
        model = User
        fields = ("password",)

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        attrs = super().validate(attrs)
        validate_password(attrs.get("password"))
        return attrs


class OTPSerializer(UserSerializer):
    class Meta:
        model = User
        fields = ("otp",)

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        attrs = super().validate(attrs)
        user = User.objects.verify_otp(attrs.get("otp"))
        if not user:
            raise AuthenticationFailed(code=status.HTTP_401_UNAUTHORIZED)
        attrs["user"] = user
        return attrs


class CreateUserSerializer(OTPSerializer, PasswordSerializer):
    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "password", "otp")

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        attrs = super().validate(attrs)
        if attrs["user"].is_active is not None:
            raise AuthenticationFailed(code=status.HTTP_401_UNAUTHORIZED)
        return attrs

    def create(self, validated_data: dict[str, Any]) -> User:
        return User.objects.create_user(
            validated_data.get("user"),
            validated_data.get("username"),
            validated_data.get("first_name"),
            validated_data.get("last_name"),
            validated_data.get("password"),
        )


class UpdatePasswordSerializer(PasswordSerializer):
    old_password = CharField(max_length=150, required=True, write_only=True)

    class Meta:
        model = User
        fields = ("password", "old_password")

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        if not self.instance.check_password(attrs.get("old_password")):
            raise AuthenticationFailed(code=status.HTTP_401_UNAUTHORIZED)
        return super().validate(attrs)

    def update(self, instance: User, validated_data: dict[str, Any]) -> User:
        Telegram().logout_after_password_change_message(instance)
        return User.objects.update_password(instance, validated_data.get("password"))


class ResetPasswordSerializer(PasswordSerializer, OTPSerializer):
    class Meta:
        model = User
        fields = ("otp", "password")

    def save(self, **kwargs: Any) -> User:
        return User.objects.reset_password(self.validated_data.get("user"), self.validated_data.get("password"))


class RequestPasswordResetSerializer(Serializer):
    email = EmailField(max_length=150, required=True)

    def _save_in_thread(self, email: str) -> None:
        # Even though the reset-password email is sent in another thread, the
        # database query and the OTP setup is executed in a different one to
        # prevet user enumerations by analyzing the Rekono execution time
        # during the password reset request
        user = User.objects.filter(email=email, is_active=True).first()
        if email and user:
            otp = User.objects.setup_otp(user)
            SMTP().reset_password(user, otp)
            self.logger.info(f"[User] User {user.id} requested a password reset", extra={"user": user.id})

    def save(self, **kwargs: Any) -> None:
        threading.Thread(target=self._save_in_thread, args=(self.validated_data.get("email"),)).start()
        return None


class EnableMfaSerializer(MfaSerializer):
    validator = User.objects.verify_mfa

    def save(self, **kwargs: Any) -> User:
        self.context.get("request").user.mfa = True
        self.context.get("request").user.save(update_fields=["mfa"])
        return self.context.get("request").user


class DisableMfaSerializer(MfaSerializer):
    def save(self, **kwargs: Any) -> User:
        self.context.get("request").user.mfa = False
        self.context.get("request").user.save(update_fields=["mfa"])
        return self.context.get("request").user


class RegisterMfaSerializer(Serializer):
    url = URLField(max_length=200, read_only=True)
