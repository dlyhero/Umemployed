from atexit import register
from django.contrib import admin

# Register your models here.
from .models import Company, Interview
from job.models import Rating
admin.site.register(Company)
admin.site.register(Interview)
admin.site.register(Rating)