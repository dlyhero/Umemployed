# Generated by Django 4.2.7 on 2024-07-25 22:39

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("resume", "0031_alter_resume_date_of_birth_userprofile"),
    ]

    operations = [
        migrations.CreateModel(
            name="Language",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("name", models.CharField(max_length=100)),
            ],
        ),
    ]
