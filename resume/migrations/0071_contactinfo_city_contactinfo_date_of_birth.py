# Generated by Django 5.1.5 on 2025-04-15 15:06

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("resume", "0070_remove_application_job_remove_application_user_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="contactinfo",
            name="city",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="contactinfo",
            name="date_of_birth",
            field=models.DateField(blank=True, null=True),
        ),
    ]
