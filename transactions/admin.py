from atexit import register

from django.contrib import admin

# Register your models here.
from .models import DailyUsage, Subscription, Transaction

admin.site.register(Transaction)
admin.site.register(DailyUsage)
admin.site.register(Subscription)
