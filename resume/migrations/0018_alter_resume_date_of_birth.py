# Generated by Django 4.2.7 on 2024-06-19 00:36

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("resume", "0017_alter_resume_date_of_birth"),
    ]

    operations = [
        migrations.AlterField(
            model_name="resume",
            name="date_of_birth",
            field=models.DateField(default="2024-06-19", null=True),
        ),
    ]
