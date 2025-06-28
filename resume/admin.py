from atexit import register
from django.contrib import admin
from .models import *

admin.site.register(Skill)
admin.site.register(SkillCategory)
admin.site.register(Resume)
admin.site.register(Education)
admin.site.register(Experience)
admin.site.register(ResumeDoc)
admin.site.register(ContactInfo)
admin.site.register(WorkExperience)
admin.site.register(UserProfile)
admin.site.register(UserLanguage)
admin.site.register(Language)
admin.site.register(ResumeAnalysis)
admin.site.register(Transcript)
admin.site.register(ResumeEnhancementTask)

from .models import EnhancedResume

@admin.register(EnhancedResume)
class EnhancedResumeAdmin(admin.ModelAdmin):
    list_display = ('user', 'job', 'full_name', 'email', 'created_at')
    search_fields = ('user__username', 'full_name', 'email')
    list_filter = ('created_at', 'job')
    