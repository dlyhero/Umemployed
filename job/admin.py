from django.contrib import admin
from .models import Job, Application,MCQ,ApplicantAnswer,SkillQuestion
# Register your models here.

admin.site.register(Job)
admin.site.register(Application)
admin.site.register(MCQ)
admin.site.register(ApplicantAnswer)
admin.site.register(SkillQuestion)
