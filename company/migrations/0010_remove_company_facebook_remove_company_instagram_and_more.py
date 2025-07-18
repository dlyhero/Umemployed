# Generated by Django 4.2.7 on 2024-09-25 13:19

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
from django_ckeditor_5.fields import CKEditor5Field


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("company", "0009_alter_company_country"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="company",
            name="facebook",
        ),
        migrations.RemoveField(
            model_name="company",
            name="instagram",
        ),
        migrations.RemoveField(
            model_name="company",
            name="twitter",
        ),
        migrations.RemoveField(
            model_name="company",
            name="vision_statement",
        ),
        migrations.AlterField(
            model_name="company",
            name="cover_photo",
            field=models.ImageField(
                blank=True,
                default="company/logos/zilotech-favicon-bgtransparent.png ",
                upload_to="company/cover_photos",
            ),
        ),
        migrations.AlterField(
            model_name="company",
            name="description",
            field=CKEditor5Field(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="company",
            name="industry",
            field=models.CharField(
                blank=True,
                choices=[
                    ("Technology", "Technology"),
                    ("Finance", "Finance"),
                    ("Healthcare", "Healthcare"),
                    ("Education", "Education"),
                    ("Manufacturing", "Manufacturing"),
                    ("Retail", "Retail"),
                    ("Hospitality", "Hospitality"),
                    ("Construction", "Construction"),
                    ("Transportation", "Transportation"),
                ],
                max_length=50,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="company",
            name="job_openings",
            field=CKEditor5Field(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="company",
            name="logo",
            field=models.ImageField(
                blank=True,
                default="company/logos/zilotech-favicon-bgtransparent.png ",
                upload_to="company/logos",
            ),
        ),
        migrations.AlterField(
            model_name="company",
            name="mission_statement",
            field=CKEditor5Field(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="company",
            name="size",
            field=models.CharField(
                blank=True,
                choices=[
                    ("1-10", "1-10 employees"),
                    ("11-50", "11-50 employees"),
                    ("51-200", "51-200 employees"),
                    ("201-500", "201-500 employees"),
                    ("501-1000", "501-1000 employees"),
                    ("1001-5000", "1001-5000 employees"),
                    ("5001-10000", "5001-10000 employees"),
                    ("10001+", "10001+ employees"),
                ],
                max_length=50,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="company",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
    ]
