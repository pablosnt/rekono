from django.db import models

from executions.models import Execution

# Create your models here.


class OSINT(models.Model):

    class DataType(models.IntegerChoices):
        IP = 1
        DOMAIN = 2
        USER = 3
        MAIL = 4
        PASSWORD = 5

    execution = models.ForeignKey(
        Execution,
        related_name='osints',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    data = models.TextField(max_length=250)
    data_type = models.IntegerField(choices=DataType.choices)
    source = models.TextField(max_length=50, blank=True, null=True)
    reference = models.TextField(max_length=250, blank=True, null=True)
    creation = models.DateTimeField(auto_now_add=True)


class Host(models.Model):

    class OSType(models.IntegerChoices):
        LINUX = 1
        WINDOWS = 2
        MACOS = 3
        IOS = 4
        ANDROID = 5
        SOLARIS = 6
        FREEBSD = 7
        OTHER = 8

    execution = models.ForeignKey(
        Execution,
        related_name='hosts',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    address = models.TextField(max_length=20)
    os = models.TextField(max_length=250, blank=True, null=True)
    os_type = models.IntegerField(
        choices=OSType.choices,
        blank=True,
        null=True
    )
    creation = models.DateTimeField(auto_now_add=True)


class Enumeration(models.Model):

    class PortStatus(models.IntegerChoices):
        OPEN = 1
        OPEN_FILTERED = 2
        FILTERED = 3
        CLOSED = 4

    class Protocol(models.IntegerChoices):
        UDP = 1
        TCP = 2

    execution = models.ForeignKey(
        Execution,
        related_name='enumerations',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    host = models.ForeignKey(Host, related_name='enumerations', on_delete=models.CASCADE)
    port = models.IntegerField()
    port_status = models.IntegerField(choices=PortStatus.choices)
    protocol = models.IntegerField(choices=Protocol.choices)
    service = models.TextField(max_length=50)
    creation = models.DateTimeField(auto_now_add=True)


class HttpEndpoint(models.Model):
    execution = models.ForeignKey(
        Execution,
        related_name='http_endpoints',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    enumeration = models.ForeignKey(
        Enumeration,
        related_name='http_endpoints',
        on_delete=models.CASCADE
    )
    endpoint = models.TextField(max_length=500)
    creation = models.DateTimeField(auto_now_add=True)


class Technology(models.Model):
    execution = models.ForeignKey(
        Execution,
        related_name='technologies',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    enumeration = models.ForeignKey(
        Enumeration,
        related_name='technologies',
        on_delete=models.CASCADE
    )
    name = models.TextField(max_length=100)
    version = models.TextField(max_length=100, blank=True, null=True)
    reference = models.TextField(max_length=250, blank=True, null=True)
    creation = models.DateTimeField(auto_now_add=True)


class Vulnerability(models.Model):

    class Severity(models.IntegerChoices):
        INFO = 1
        LOW = 2
        MEDIUM = 3
        HIGH = 4
        CRITICAL = 5

    execution = models.ForeignKey(
        Execution,
        related_name='vulnerabilities',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    enumeration = models.ForeignKey(
        Enumeration,
        related_name='vulnerabilities',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    technology = models.ForeignKey(
        Technology,
        related_name='vulnerabilities',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    name = models.TextField(max_length=50)
    description = models.TextField(blank=True, null=True)
    severity = models.IntegerField(choices=Severity.choices)
    cve = models.TextField(max_length=20, blank=True, null=True)
    reference = models.TextField(max_length=250, blank=True, null=True)
    creation = models.DateTimeField(auto_now_add=True)


class Exploit(models.Model):
    execution = models.ForeignKey(
        Execution,
        related_name='exploits',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    vulnerability = models.ForeignKey(
        Vulnerability,
        related_name='exploits',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    technology = models.ForeignKey(
        Technology,
        related_name='exploits',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    name = models.TextField(max_length=100)
    description = models.TextField(blank=True, null=True)
    reference = models.TextField(max_length=250)
    checked = models.BooleanField(default=False)
    creation = models.DateTimeField(auto_now_add=True)
