from atexit import register

from django.contrib import admin

from .models import (
    MCQ,
    ApplicantAnswer,
    Application,
    CompletedSkills,
    Job,
    RetakeRequest,
    SavedJob,
    Shortlist,
    SkillQuestion,
)

# Register your models here.

admin.site.register(Job)
admin.site.register(Application)
admin.site.register(MCQ)
admin.site.register(ApplicantAnswer)
admin.site.register(SkillQuestion)
admin.site.register(SavedJob)
admin.site.register(CompletedSkills)
admin.site.register(Shortlist)
admin.site.register(RetakeRequest)
