from django.db import models


class Notification(models.IntegerChoices):
    MAIL = 1
    TELEGRAM = 2
