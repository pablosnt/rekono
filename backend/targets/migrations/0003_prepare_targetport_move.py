# Brings the target ports table to its version 2.x shape and name while this app still owns the
# model, so target_ports.0001_initial can adopt it instead of recreating it and losing every port

import django.core.validators
import security.validators.enums
import security.validators.input_validator
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('targets', '0002_auto_20230108_1356'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='targetport',
            name='unique target port',
        ),
        migrations.AddField(
            model_name='targetport',
            name='path',
            field=models.TextField(blank=True, max_length=100, null=True, validators=[security.validators.input_validator.Validator(security.validators.enums.Regex['PATH'], code='path')]),
        ),
        migrations.AlterField(
            model_name='targetport',
            name='port',
            field=models.IntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(65535)]),
        ),
        migrations.AddConstraint(
            model_name='targetport',
            constraint=models.UniqueConstraint(fields=('target', 'port'), name='unique_target_port'),
        ),
        migrations.AlterModelTable(
            name='targetport',
            table='target_ports_targetport',
        ),
    ]
