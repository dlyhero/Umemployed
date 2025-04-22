from rest_framework import serializers
from ..models import Job, Application, SavedJob

class JobSerializer(serializers.ModelSerializer):
    is_saved = serializers.SerializerMethodField()
    is_applied = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = [
            'id', 'title', 'hire_number', 'job_location_type', 'job_type', 
            'location', 'salary_range', 'category', 'description', 
            'responsibilities', 'benefits', 'requirements', 'level', 
            'experience_levels', 'weekly_ranges', 'shifts', 'created_at', 
            'is_saved', 'is_applied'
        ]
        extra_kwargs = {
            'description': {'required': False},
            'responsibilities': {'required': False},
            'benefits': {'required': False},
            'requirements': {'required': False},
            'level': {'required': False},
            'experience_levels': {'required': False},
            'weekly_ranges': {'required': False},
            'shifts': {'required': False},
        }

    def get_is_saved(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return SavedJob.objects.filter(user=user, job=obj).exists()
        return False

    def get_is_applied(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return Application.objects.filter(user=user, job=obj).exists()
        return False

class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ['id', 'job', 'quiz_score', 'matching_percentage', 'status', 'created_at']

class SavedJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedJob
        fields = ['id', 'job', 'saved_at']
