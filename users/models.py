from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)

    email = models.EmailField(unique = True)
    is_recruiter = models.BooleanField(default=False)
    is_applicant = models.BooleanField(default=True)

    has_resume = models.BooleanField(default=False)
    has_company = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)  # Add this line
    updated_at = models.DateTimeField(auto_now=True)
