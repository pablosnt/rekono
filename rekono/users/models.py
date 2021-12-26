from typing import Any, Optional

from django.contrib.auth.models import AbstractUser, Group, UserManager
from django.db import models
from rest_framework.authtoken.models import Token
from security.authorization.roles import Role
from security.crypto import generate_otp
from users.enums import Notification
from users.mail import send_invitation_to_new_user, send_password_reset

# Create your models here.


class RekonoUserManager(UserManager):

    def create_user(self, email: str, role: Role, rekono_address: str) -> Any:
        user = User.objects.create(email=email, otp=generate_otp(), is_active=False)
        group = Group.objects.get(name=role.value)
        if not group:
            group = Group.objects.get(name=Role.READER)
        user.groups.clear()
        user.groups.set([group])
        user.save()
        api_token = Token.objects.create(user=user)
        api_token.save()
        send_invitation_to_new_user(user, rekono_address)
        return user

    def create_superuser(
        self,
        username: str,
        email: Optional[str],
        password: Optional[str],
        **extra_fields: Any
    ) -> Any:
        user = super().create_superuser(username, email, password, **extra_fields)
        group = Group.objects.get(name=Role.ADMIN)
        user.groups.set([group])
        user.save()
        api_token = Token.objects.create(user=user)
        api_token.save()
        return user

    def change_user_role(self, user: Any, role: Role) -> Any:
        group = Group.objects.get(name=role.value)
        if group:
            user.groups.clear()
            user.groups.set([group])
            user.save()
        return user

    def enable_user(self, user: Any, role: Role, rekono_address: str) -> Any:
        user.is_active = True
        user.otp = generate_otp()
        group = Group.objects.get(name=role.value)
        if not group:
            group = Group.objects.get(name=Role.READER)
        user.groups.clear()
        user.groups.set([group])
        user.save()
        api_token = Token.objects.create(user=user)
        api_token.save()
        send_password_reset(user, rekono_address)
        return user

    def disable_user(self, user: Any) -> Any:
        user.is_active = False
        user.set_unusable_password()
        user.otp = None
        user.groups.clear()
        user.save()
        try:
            token = Token.objects.get(user=user)
            token.delete()
        except Token.DoesNotExist:
            pass
        return user

    def request_password_reset(self, user: Any, rekono_address: str) -> Any:
        user.otp = generate_otp()
        user.save()
        send_password_reset(user, rekono_address)
        return user


class User(AbstractUser):
    username = models.TextField(max_length=150, unique=True, blank=True, null=True)
    first_name = models.TextField(max_length=150, blank=True, null=True)
    last_name = models.TextField(max_length=150, blank=True, null=True)
    email = models.EmailField(max_length=150, unique=True)

    otp = models.TextField(max_length=200, unique=True, blank=True, null=True)

    notification_preference = models.TextField(
        max_length=10,
        choices=Notification.choices,
        default=Notification.EMAIL,
        blank=True,
        null=True
    )
    telegram_id = models.IntegerField(blank=True, null=True)

    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['email']
    objects = RekonoUserManager()

    class Meta:
        ordering = ['-id']

    def __str__(self) -> str:
        return self.email

    def get_project(self) -> Any:
        return None
