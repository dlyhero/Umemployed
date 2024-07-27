from django.contrib import admin

# Register your models here.
from .models import *
admin.site.register(Assessment)
admin.site.register(Question)
admin.site.register(Session)
admin.site.register(Result)
admin.site.register(Option)