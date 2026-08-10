# Deletes the version 1.x system model, split from the generated migration that created the
# settings one, so settings.0003_migrate_1x_configuration can read its configuration first

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('settings', '0003_migrate_1x_configuration'),
    ]

    operations = [
        migrations.DeleteModel(
            name='System',
        ),
    ]
