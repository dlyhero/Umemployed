# Generated by Django 4.2.7 on 2024-06-04 11:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("resume", "0012_remove_resume_category_alter_resume_date_of_birth"),
    ]

    operations = [
        migrations.AddField(
            model_name="resume",
            name="category",
            field=models.ForeignKey(
                default="1",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="resume.skillcategory",
            ),
        ),
    ]
