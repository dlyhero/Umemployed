# Generated by Django 5.1.1 on 2024-10-14 11:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("message", "0004_message_idd"),
    ]

    operations = [
        migrations.AddField(
            model_name="message",
            name="replyTo",
            field=models.ForeignKey(
                blank=True,
                default=None,
                null=True,
                on_delete=django.db.models.deletion.SET_DEFAULT,
                related_name="replies",
                to="message.message",
            ),
        ),
    ]
