# Generated by Django 4.2.7 on 2024-08-11 15:55

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("resume", "0041_alter_skill_user"),
    ]

    operations = [
        migrations.AlterField(
            model_name="resume",
            name="date_of_birth",
            field=models.DateField(default="2024-08-11", null=True),
        ),
    ]
