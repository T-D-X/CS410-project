from __future__ import annotations

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pipeline", "0001_initial"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="resumedocument",
            index=models.Index(fields=["file_name"], name="resume_file_name_idx"),
        ),
    ]
