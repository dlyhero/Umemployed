# Generated by Django 4.2.7 on 2024-09-25 15:01

import django_countries.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("company", "0010_remove_company_facebook_remove_company_instagram_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="company",
            name="country",
            field=django_countries.fields.CountryField(max_length=2),
        ),
        migrations.AlterField(
            model_name="company",
            name="founded",
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
