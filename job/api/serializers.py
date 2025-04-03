from rest_framework import serializers
from ..models import Job, Application, SavedJob

class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = [
            'id', 'title', 'hire_number', 'job_location_type', 'job_type', 
            'location', 'salary_range', 'category', 'description', 
            'responsibilities', 'benefits', 'requirements', 'level', 
            'experience_levels', 'weekly_ranges', 'shifts', 'created_at'
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

class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ['id', 'job', 'quiz_score', 'matching_percentage', 'status', 'created_at']

class SavedJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedJob
        fields = ['id', 'job', 'saved_at']
