# Generated by Django 3.2.16 on 2023-01-08 12:56

from django.db import migrations, models
import django.db.models.deletion
import input_types.base
import security.input_validation


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('targets', '0002_auto_20230108_1356'),
    ]

    operations = [
        migrations.CreateModel(
            name='Authentication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(max_length=100, validators=[security.input_validation.validate_name])),
                ('credential', models.TextField(max_length=500, validators=[security.input_validation.validate_credential])),
                ('type', models.TextField(choices=[('Basic', 'Basic'), ('Bearer', 'Bearer'), ('Cookie', 'Cookie'), ('Digest', 'Digest'), ('JWT', 'Jwt'), ('NTLM', 'Ntlm')], max_length=8)),
                ('target_port', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='authentication', to='targets.targetport')),
            ],
            bases=(models.Model, input_types.base.BaseInput),
        ),
    ]
