import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)

    email = models.EmailField(unique = True)
    is_recruiter = models.BooleanField(default=False)
    is_applicant = models.BooleanField(default=True)

    has_resume = models.BooleanField(default=False)
    has_company = models.BooleanField(default=False)
