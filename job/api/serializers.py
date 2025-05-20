from rest_framework import serializers
from ..models import Job, Application, SavedJob, Company

class JobSerializer(serializers.ModelSerializer):
    is_saved = serializers.SerializerMethodField()
    is_applied = serializers.SerializerMethodField()
    company = serializers.SerializerMethodField()
    has_started = serializers.SerializerMethodField()
    requirements = serializers.SerializerMethodField()  # Override requirements field

    class Meta:
        model = Job
        fields = [
            'id', 'title', 'hire_number', 'job_location_type', 'job_type', 
            'location', 'salary_range', 'category', 'description', 
            'responsibilities', 'benefits', 'requirements', 'level', 
            'experience_levels', 'weekly_ranges', 'shifts', 'created_at', 
            'is_saved', 'is_applied', 'company', 'has_started'
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
        request = self.context.get('request', None)
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            return SavedJob.objects.filter(user=request.user, job=obj).exists()
        return False

    def get_is_applied(self, obj):
        request = self.context.get('request', None)
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            return Application.objects.filter(user=request.user, job=obj).exists()
        return False

    def get_company(self, obj):
        return {
            "id": obj.company.id,
            "name": obj.company.name,
            "location": obj.company.location,
            "description": obj.company.description,
            "industry": obj.company.industry,
            "size": obj.company.size,
            "founded": obj.company.founded,
            "website_url": obj.company.website_url,
            "country": obj.company.country.code if obj.company.country else None,
            "country_name": obj.company.country.name if obj.company.country else None,
            "contact_email": obj.company.contact_email,
            "contact_phone": obj.company.contact_phone,
            "linkedin": obj.company.linkedin,
            "video_introduction": obj.company.video_introduction,
            "logo": obj.company.logo.url if obj.company.logo else None,
            "cover_photo": obj.company.cover_photo.url if obj.company.cover_photo else None,
            "mission_statement": obj.company.mission_statement,
            "job_openings": obj.company.job_openings,
        }

    def get_has_started(self, obj):
        request = self.context.get('request', None)
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            application = Application.objects.filter(user=request.user, job=obj).first()
            return application.has_started if application else False
        return False

    def get_requirements(self, obj):
        # Return list of {id, name} for each requirement (skill)
        return [
            {"id": skill.id, "name": skill.name}
            for skill in obj.requirements.all()
        ]

class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ['id', 'job', 'quiz_score', 'matching_percentage', 'status', 'created_at']

class SavedJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedJob
        fields = ['id', 'job', 'saved_at']
