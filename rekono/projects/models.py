from django.contrib.auth.models import User
from django.db import models
from django.db.models.deletion import CASCADE

# Create your models here.


class Project(models.Model):
    name = models.TextField(max_length=50)
    description = models.TextField(max_length=250)
    owner = models.ForeignKey(User, on_delete=CASCADE)
    members = models.ManyToManyField(
        User,
        through='ProjectMember',
        related_name='members',
        blank=True
    )

    def __str__(self) -> str:
        return self.name


class Target(models.Model):

    class TargetType(models.IntegerChoices):
        PRIVATE_IP = 1
        PUBLIC_IP = 2
        NETWORK = 3
        IP_RANGE = 4
        DOMAIN = 5

    project = models.ForeignKey(
        Project,
        related_name='targets',
        on_delete=models.CASCADE
    )
    target = models.TextField(max_length=100)
    type = models.IntegerField(choices=TargetType.choices)

    def __str__(self) -> str:
        return self.target


class TargetPort(models.Model):
    target = models.ForeignKey(
        Target,
        related_name='target_ports',
        on_delete=models.CASCADE
    )
    port = models.IntegerField()

    def __str__(self) -> str:
        return f'{self.target.target} - {self.port}'


class ProjectMember(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f'{self.user.username} - {self.project.name}'
