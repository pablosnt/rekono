from django.contrib.auth.models import AbstractUser, UserManager, Group
from django.db import models
from rest_framework.authtoken.models import Token
from authorization.groups.roles import Role
from users import otp_generator
from typing import Any, Optional
from integrations.mail import sender

# Create your models here.


class RekonoUserManager(UserManager):

    def create_user(self, email: str, role: Role, domain: str) -> Any:
        user = User.objects.create(email=email, otp=otp_generator.generate_otp(), is_active=False)
        group = Group.objects.get(name=role.name.capitalize())
        if not group:
            group = Group.objects.get(name=Role.READER.name.capitalize())
        user.groups.clear()
        user.groups.set([group])
        user.save()
        api_token = Token.objects.create(user=user)
        api_token.save()
        sender.send_invitation_to_new_user(user, domain)
        return user

    def create_superuser(
        self,
        username: str,
        email: Optional[str],
        password: Optional[str],
        **extra_fields: Any
    ) -> Any:
        user = super().create_superuser(username, email, password, **extra_fields)
        group = Group.objects.get(name=Role.ADMIN.name.capitalize())
        user.groups.set([group])
        user.save()
        api_token = Token.objects.create(user=user)
        api_token.save()
        return user

    def disable_user(self, user: Any) -> None:
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

class User(AbstractUser):
    username = models.TextField(max_length=150, unique=True, blank=True, null=True)
    first_name = models.TextField(max_length=150, blank=True, null=True)
    last_name = models.TextField(max_length=150, blank=True, null=True)
    email = models.EmailField(max_length=150, unique=True)

    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['email']
    objects = RekonoUserManager()

    otp = models.TextField(max_length=200, blank=True, null=True)

    class Notification(models.IntegerChoices):
        MAIL = 1
        TELEGRAM = 2

    notification_preference = models.IntegerField(
        choices=Notification.choices,
        default=Notification.MAIL,
        blank=True,
        null=True
    )
    telegram_token = models.TextField(max_length=100, blank=True, null=True)

    binaryedge_apikey = models.TextField(max_length=100, blank=True, null=True)
    bing_apikey = models.TextField(max_length=100, blank=True, null=True)
    censys_apikey = models.TextField(max_length=100, blank=True, null=True)
    github_apikey = models.TextField(max_length=100, blank=True, null=True)
    hunter_apikey = models.TextField(max_length=100, blank=True, null=True)
    intelx_apikey = models.TextField(max_length=100, blank=True, null=True)
    pentestTools_apikey = models.TextField(max_length=100, blank=True, null=True)
    projectDiscovery_apikey = models.TextField(max_length=100, blank=True, null=True)
    rocketreach_apikey = models.TextField(max_length=100, blank=True, null=True)
    securityTrails_apikey = models.TextField(max_length=100, blank=True, null=True)
    shodan_apikey = models.TextField(max_length=100, blank=True, null=True)
    spyse_apikey = models.TextField(max_length=100, blank=True, null=True)
    zoomeye_apikey = models.TextField(max_length=100, blank=True, null=True)

    def __str__(self) -> str:
        return self.email
