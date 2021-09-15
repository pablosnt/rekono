from django.contrib.auth.models import User
from django.db import models

# Create your models here.


class UserDetail(models.Model):

    class Notification(models.IntegerChoices):
        MAIL = 1
        TELEGRAM = 2

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    notification_preference = models.IntegerField(
        choices=Notification.choices,
        default=Notification.MAIL,
        blank=True,
        null=True
    )
    telegram_token = models.TextField(max_length=50, blank=True, null=True)
