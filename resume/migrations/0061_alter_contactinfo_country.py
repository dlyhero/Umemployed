# Generated by Django 4.2.7 on 2025-01-19 13:46

import django_countries.fields
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("resume", "0060_alter_education_degree_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="contactinfo",
            name="country",
            field=django_countries.fields.CountryField(default="US", max_length=2),
        ),
    ]
