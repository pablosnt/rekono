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
    telegram_token = models.TextField(max_length=100, blank=True, null=True)
    binaryedge_apikey = models.TextField(max_length=100, blank=True, null=True)
    bing_apikey = models.TextField(max_length=100, blank=True, null=True)
    censys_apikey = models.TextField(max_length=100, blank=True, null=True)
    github_apikey = models.TextField(max_length=100, blank=True, null=True)
    hunter_apikey = models.TextField(max_length=100, blank=True, null=True)
    intelx_apikey = models.TextField(max_length=100, blank=True, null=True)
    pentestTools_apikey = models.TextField(max_length=100, blank=True, null=True)
    rocketreach_apikey = models.TextField(max_length=100, blank=True, null=True)
    securityTrails_apikey = models.TextField(max_length=100, blank=True, null=True)
    shodan_apikey = models.TextField(max_length=100, blank=True, null=True)
    spyse_apikey = models.TextField(max_length=100, blank=True, null=True)
    zoomeye_apikey = models.TextField(max_length=100, blank=True, null=True)
