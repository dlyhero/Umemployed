import random
import string
import uuid

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django_ckeditor_5.fields import CKEditor5Field
from django_countries.fields import CountryField

from users.models import User

User = get_user_model()


class Company(models.Model):
    INDUSTRY_CHOICES = [
        ("Technology", "Technology"),
        ("Finance", "Finance"),
        ("Healthcare", "Healthcare"),
        ("Education", "Education"),
        ("Manufacturing", "Manufacturing"),
        ("Retail", "Retail"),
        ("Hospitality", "Hospitality"),
        ("Construction", "Construction"),
        ("Transportation", "Transportation"),
    ]

    SIZE_CHOICES = [
        ("1-10", "1-10 employees"),
        ("11-50", "11-50 employees"),
        ("51-200", "51-200 employees"),
        ("201-500", "201-500 employees"),
        ("501-1000", "501-1000 employees"),
        ("1001-5000", "1001-5000 employees"),
        ("5001-10000", "5001-10000 employees"),
        ("10001+", "10001+ employees"),
    ]

    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="company")
    # Basic Information
    name = models.CharField(max_length=100, null=True, blank=True)
    industry = models.CharField(max_length=50, choices=INDUSTRY_CHOICES, null=True, blank=True)
    size = models.CharField(max_length=50, choices=SIZE_CHOICES, null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    founded = models.IntegerField(null=True, blank=True)
    website_url = models.URLField(max_length=200, null=True, blank=True)
    country = CountryField(blank_label="(select country)")

    # Contact Information
    contact_email = models.EmailField(null=True, blank=True)
    contact_phone = models.CharField(max_length=20, null=True, blank=True)

    # Description with CKEditor
    description = CKEditor5Field(null=True, blank=True)
    mission_statement = CKEditor5Field(null=True, blank=True)

    linkedin = models.URLField(blank=True, null=True)
    video_introduction = models.URLField(blank=True, null=True)

    # Media
    logo = models.ImageField(
        upload_to="company/logos", blank=True, default="resume/images/default.jpg"
    )
    cover_photo = models.ImageField(
        upload_to="company/cover_photos", blank=True, default="resume/images/default.jpg"
    )

    # Job Openings with CKEditor
    job_openings = CKEditor5Field(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name if self.name else "Unnamed Company"


import pytz


class Interview(models.Model):
    INTERVIEW_TYPES = [
        ('custom', 'Custom Video Chat'),
        ('google_meet', 'Google Meet'),
    ]
    
    candidate = models.ForeignKey(User, on_delete=models.CASCADE)
    recruiter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='interviews_created', null=True, blank=True)
    interview_type = models.CharField(max_length=20, choices=INTERVIEW_TYPES, default='custom')
    date = models.DateField()
    time = models.TimeField()
    timezone = models.CharField(max_length=50, default="UTC")
    meeting_link = models.URLField()
    room_id = models.CharField(max_length=8, unique=True, editable=False)
    google_event_id = models.CharField(max_length=255, null=True, blank=True, help_text="Google Calendar event ID")
    note = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.room_id:
            self.room_id = self.generate_room_id()
        super().save(*args, **kwargs)

    def generate_room_id(self):
        return "".join(random.choices(string.ascii_uppercase + string.digits, k=8))

    def __str__(self):
        return f"Interview with {self.candidate.username} on {self.date} at {self.time} ({self.timezone})"


class GoogleCredentials(models.Model):
    """Store Google OAuth credentials for users"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='google_credentials')
    credentials_json = models.TextField(help_text="JSON-encoded Google OAuth credentials")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Google credentials for {self.user.email}"

    class Meta:
        verbose_name_plural = "Google Credentials"


class OAuthState(models.Model):
    """Temporary storage for OAuth state parameters"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    state = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['state']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"OAuth State for {self.user.email}: {self.state[:20]}..."
