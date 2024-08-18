from django.db import models
from users.models import User
import uuid
from django.contrib.auth import get_user_model
from django_countries.fields import CountryField

User = get_user_model()


class Company(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # Basic Information
    name = models.CharField(max_length=100, null=True, blank=True)
    industry = models.CharField(max_length=50, null=True, blank=True)
    size = models.CharField(max_length=50, null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    founded = models.PositiveIntegerField(null=True, blank=True)
    website_url = models.URLField(max_length=200, null=True, blank=True)
    country = CountryField()
    
    # Contact Information
    contact_email = models.EmailField(null=True, blank=True)
    contact_phone = models.CharField(max_length=20, null=True, blank=True)
    
    # Description
    description = models.TextField(null=True, blank=True)
    mission_statement = models.TextField(null=True, blank=True)
    vision_statement = models.TextField(null=True, blank=True)
    
    # Social Media
    linkedin = models.URLField(max_length=200, null=True, blank=True)
    facebook = models.URLField(max_length=200, null=True, blank=True)
    twitter = models.URLField(max_length=200, null=True, blank=True)
    instagram = models.URLField(max_length=200, null=True, blank=True)
    
    # Media
    logo = models.ImageField(upload_to="company/logos", blank=True, default="company/logos/default_logo.jpg")
    cover_photo = models.ImageField(upload_to="company/cover_photos", blank=True, default="company/cover_photos/default_cover.jpg")
    video_introduction = models.URLField(max_length=200, null=True, blank=True)
    
    # Job Openings
    job_openings = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name if self.name else "Unnamed Company"

