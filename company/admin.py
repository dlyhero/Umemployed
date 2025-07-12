from atexit import register

from django.contrib import admin

from job.models import Rating

# Register your models here.
from .models import Company, Interview, GoogleCredentials, OAuthState


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'industry', 'size', 'created_at')
    list_filter = ('industry', 'size', 'created_at')
    search_fields = ('name', 'user__email', 'user__username')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    list_display = ('candidate', 'recruiter', 'interview_type', 'date', 'time', 'created_at')
    list_filter = ('interview_type', 'date', 'created_at')
    search_fields = ('candidate__email', 'candidate__username', 'recruiter__email')
    readonly_fields = ('room_id', 'created_at')


@admin.register(GoogleCredentials)
class GoogleCredentialsAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'updated_at')
    search_fields = ('user__email', 'user__username')
    readonly_fields = ('created_at', 'updated_at', 'credentials_json')
    
    def has_change_permission(self, request, obj=None):
        # Prevent editing credentials for security
        return False


@admin.register(OAuthState)
class OAuthStateAdmin(admin.ModelAdmin):
    list_display = ('user', 'state_preview', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'user__username', 'state')
    readonly_fields = ('state', 'created_at')
    
    def state_preview(self, obj):
        return f"{obj.state[:20]}..." if len(obj.state) > 20 else obj.state
    state_preview.short_description = 'State (preview)'
    
    def has_change_permission(self, request, obj=None):
        # OAuth states shouldn't be edited
        return False


admin.site.register(Rating)
