from django.db import models


class TargetType(models.IntegerChoices):
    PRIVATE_IP = 1
    PUBLIC_IP = 2
    NETWORK = 3
    IP_RANGE = 4
    DOMAIN = 5
