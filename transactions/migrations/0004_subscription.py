# Generated by Django 5.1.5 on 2025-05-20 14:45

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("transactions", "0003_transaction_candidate_alter_transaction_user"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Subscription",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "user_type",
                    models.CharField(
                        choices=[("user", "User"), ("recruiter", "Recruiter")],
                        max_length=10,
                    ),
                ),
                (
                    "tier",
                    models.CharField(
                        choices=[
                            ("basic", "Basic"),
                            ("standard", "Standard"),
                            ("premium", "Premium"),
                            ("custom", "Custom"),
                        ],
                        max_length=10,
                    ),
                ),
                ("is_active", models.BooleanField(default=True)),
                (
                    "stripe_subscription_id",
                    models.CharField(blank=True, max_length=100, null=True),
                ),
                ("started_at", models.DateTimeField(auto_now_add=True)),
                ("ended_at", models.DateTimeField(blank=True, null=True)),
                ("daily_limit", models.IntegerField(blank=True, null=True)),
                ("custom_inquiry", models.TextField(blank=True, null=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="subscriptions",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
