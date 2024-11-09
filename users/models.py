from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    is_recruiter = models.BooleanField(default=False)
    is_applicant = models.BooleanField(default=True)
    has_resume = models.BooleanField(default=False)
    has_company = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return self.email