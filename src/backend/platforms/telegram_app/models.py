from django.db import models
from django.db.models import Q
from framework.models import BaseEncrypted, BaseModel
from rekono.settings import AUTH_USER_MODEL
from security.authorization.roles import Role
from security.input_validator import FutureDatetimeValidator, Regex, Validator
from users.models import User

# Create your models here.


class TelegramSettings(BaseEncrypted):
    _token = models.TextField(
        max_length=200,
        validators=[Validator(Regex.SECRET.value, code="api_token")],
        null=True,
        blank=True,
        db_column="token",
    )

    _encrypted_field = "_token"


class TelegramChat(BaseModel):
    user = models.OneToOneField(
        AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="telegram_chat",
        blank=True,
        null=True,
    )
    chat_id = models.IntegerField(unique=True)
    creation = models.DateTimeField(auto_now_add=True)
    # One Time Password to link user account
    otp = models.TextField(max_length=200, blank=True, null=True)
    otp_expiration = models.DateTimeField(
        blank=True,
        null=True,
        validators=[FutureDatetimeValidator(code="otp_expiration")],
    )

    def is_auditor(self) -> bool:
        return (
            self.user.groups.filter(
                Q(name=str(Role.AUDITOR)) | Q(name=str(Role.ADMIN))
            ).exists()
            if self.user
            else False
        )

    def __str__(self) -> str:
        return self.user.__str__()
