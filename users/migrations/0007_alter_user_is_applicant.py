# Generated by Django 5.1.5 on 2025-04-03 08:49

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0006_alter_user_managers"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="is_applicant",
            field=models.BooleanField(default=False),
        ),
    ]
