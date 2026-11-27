from typing import Any

from django.db import migrations


def update_defectdojo_icon(apps: Any, schema_editor: Any) -> None:
    """Set the DefectDojo integration icon to the one of their new brand image.

    Reverting the migration keeps the new icon, since the previous one won't stay
    available on the DefectDojo website.

    Args:
        apps: Registry of the historical models, given by the migration framework.
        schema_editor: Not used, since only data is updated.
    """
    apps.get_model("integrations", "Integration").objects.filter(key="defectdojo").update(
        icon="https://defectdojo.com/hubfs/DD-favicon-512x512.png"
    )


class Migration(migrations.Migration):

    dependencies = [
        ("integrations", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(update_defectdojo_icon, migrations.RunPython.noop),
    ]
