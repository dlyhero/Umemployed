# Generated by Django 4.2.7 on 2024-06-04 11:29

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("resume", "0011_skill_user_alter_resume_date_of_birth"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="resume",
            name="category",
        ),
        migrations.AlterField(
            model_name="resume",
            name="date_of_birth",
            field=models.DateField(default="2024-06-04", null=True),
        ),
    ]
