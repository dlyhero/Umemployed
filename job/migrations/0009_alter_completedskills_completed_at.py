# Generated by Django 4.2.7 on 2024-06-26 02:04

import datetime

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("job", "0008_completedskills"),
    ]

    operations = [
        migrations.AlterField(
            model_name="completedskills",
            name="completed_at",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2024, 6, 26, 2, 4, 51, 723302, tzinfo=datetime.timezone.utc
                )
            ),
        ),
    ]
