# Generated by Django 4.2.7 on 2024-07-07 00:46

import datetime

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("job", "0014_job_experience_levels_job_job_location_type_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="completedskills",
            name="completed_at",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2024, 7, 7, 0, 46, 24, 238126, tzinfo=datetime.timezone.utc
                )
            ),
        ),
    ]
