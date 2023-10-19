from django.db import models
from framework.models import BaseModel
from rekono.settings import AUTH_USER_MODEL
from security.utils.input_validator import Regex, Validator
from users.models import User

# Create your models here.


class TelegramSettings(BaseModel):
    # TODO: encrypt and decrypt secret for more security
    token = models.TextField(
        max_length=200,
        validators=[Validator(Regex.SECRET.value, code="api_token")],
        null=True,
        blank=True,
    )


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
    otp = models.TextField(max_length=200, unique=True, blank=True, null=True)
    otp_expiration = models.DateTimeField(
        default=User.objects.get_otp_expiration_time, blank=True, null=True
    )

    def __str__(self) -> str:
        return self.user.__str__()
