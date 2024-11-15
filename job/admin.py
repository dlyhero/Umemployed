from atexit import register
from django.contrib import admin
from .models import Job, Application,MCQ,ApplicantAnswer, Shortlist,SkillQuestion,SavedJob,CompletedSkills,Shortlist
# Register your models here.

admin.site.register(Job)
admin.site.register(Application)
admin.site.register(MCQ)
admin.site.register(ApplicantAnswer)
admin.site.register(SkillQuestion)
admin.site.register(SavedJob)
admin.site.register(CompletedSkills)
admin.site.register(Shortlist)