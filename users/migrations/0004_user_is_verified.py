# Generated by Django 4.2.7 on 2024-10-12 21:20

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0003_alter_user_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="is_verified",
            field=models.BooleanField(default=False),
        ),
    ]
