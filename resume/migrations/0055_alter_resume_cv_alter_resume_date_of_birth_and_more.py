# Generated by Django 4.2.7 on 2024-09-25 04:13

import datetime

import django.core.validators
from django.db import migrations, models

import resume.models


class Migration(migrations.Migration):
    dependencies = [
        ("resume", "0054_alter_resume_date_of_birth"),
    ]

    operations = [
        migrations.AlterField(
            model_name="resume",
            name="cv",
            field=models.FileField(
                blank=True,
                default=" resume/cv/Nyuydine_CV_Resume.pdf",
                upload_to="resume/cv",
                validators=[
                    django.core.validators.FileExtensionValidator(["pdf"]),
                    resume.models.validate_file_mime_type,
                ],
            ),
        ),
        migrations.AlterField(
            model_name="resume",
            name="date_of_birth",
            field=models.DateField(default=datetime.date.today, null=True),
        ),
        migrations.AlterField(
            model_name="resume",
            name="profile_image",
            field=models.ImageField(
                blank=True, default="resume/images/default.jpg", upload_to="resume/images"
            ),
        ),
    ]
