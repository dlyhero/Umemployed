from rest_framework import serializers
from ..models import Company

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = [
            'id', 'name', 'industry', 'size', 'location', 'founded', 'website_url',
            'country', 'contact_email', 'contact_phone', 'description', 'mission_statement',
            'linkedin', 'video_introduction', 'logo', 'cover_photo', 'job_openings',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'logo': {'required': False},
            'cover_photo': {'required': False},
        }
