from django.db import models

# Create your enums here.


class IntensityRank(models.IntegerChoices):
    SNEAKY = 1
    LOW = 2
    NORMAL = 3
    HARD = 4
    INSANE = 5


class FindingType(models.TextChoices):
    TARGET = 'projects.models.Target'
    TARGET_PORT = 'projects.models.TargetPort'
    OSINT = 'findings.models.OSINT'
    HOST = 'findings.models.Host'
    ENUMERATION = 'findings.models.Enumeration'
    HTTP_ENDPOINT = 'findings.models.HttpEndpoint'
    TECHNOLOGY = 'findings.models.Technology'
    VULNERABILITY = 'findings.models.Vulnerability'
    EXPLOIT = 'findings.models.Exploit'
