from django.db import models
from users.models import User
import uuid
from django.contrib.auth import get_user_model
from django_countries.fields import CountryField
from ckeditor.fields import RichTextField
from django.conf import settings


User = get_user_model()



from django.db import models
from django_countries.fields import CountryField
from ckeditor.fields import RichTextField

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
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    # Basic Information
    name = models.CharField(max_length=100, null=True, blank=True)
    industry = models.CharField(max_length=50, choices=INDUSTRY_CHOICES, null=True, blank=True)
    size = models.CharField(max_length=50, choices=SIZE_CHOICES, null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    founded = models.IntegerField(null=True, blank=True) 
    website_url = models.URLField(max_length=200, null=True, blank=True)
    country = CountryField(blank_label='(select country)') 

    # Contact Information
    contact_email = models.EmailField(null=True, blank=True)
    contact_phone = models.CharField(max_length=20, null=True, blank=True)

    # Description with CKEditor
    description = RichTextField(null=True, blank=True)
    mission_statement = RichTextField(null=True, blank=True)

    linkedin = models.URLField(blank=True, null=True)
    video_introduction = models.URLField(blank=True, null=True)

    # Media
    logo = models.ImageField(upload_to="company/logos", blank=True, default="company/logos/zilotech-favicon-bgtransparent.png ")
    cover_photo = models.ImageField(upload_to="company/cover_photos", blank=True, default="company/logos/zilotech-favicon-bgtransparent.png ")

    # Job Openings with CKEditor
    job_openings = RichTextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name if self.name else "Unnamed Company"
