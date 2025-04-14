from rest_framework import serializers
from resume.models import (
    Resume, ResumeDoc, Transcript, SkillCategory, Skill, Education, Experience, 
    ContactInfo, WorkExperience, UserProfile, Language, UserLanguage, ResumeAnalysis, ProfileView
)

class SkillCategorySerializer(serializers.ModelSerializer):
    """
    Serializer for the SkillCategory model.
    Converts SkillCategory model instances to JSON and validates input data.
    """
    class Meta:
        model = SkillCategory
        fields = '__all__'

class SkillSerializer(serializers.ModelSerializer):
    """
    Serializer for the Skill model.
    Converts Skill model instances to JSON and validates input data.
    """
    class Meta:
        model = Skill
        fields = '__all__'

class EducationSerializer(serializers.ModelSerializer):
    """
    Serializer for the Education model.
    Converts Education model instances to JSON and validates input data.
    """
    class Meta:
        model = Education
        fields = '__all__'

class ExperienceSerializer(serializers.ModelSerializer):
    """
    Serializer for the Experience model.
    Converts Experience model instances to JSON and validates input data.
    """
    class Meta:
        model = Experience
        fields = '__all__'

class ResumeSerializer(serializers.ModelSerializer):
    """
    Serializer for the Resume model.
    Converts Resume model instances to JSON and validates input data.
    """
    class Meta:
        model = Resume
        fields = '__all__'

class ResumeDocSerializer(serializers.ModelSerializer):
    """
    Serializer for the ResumeDoc model.
    Converts ResumeDoc model instances to JSON and validates input data.
    """
    class Meta:
        model = ResumeDoc
        fields = '__all__'

class TranscriptSerializer(serializers.ModelSerializer):
    """
    Serializer for the Transcript model.
    Converts Transcript model instances to JSON and validates input data.
    """
    class Meta:
        model = Transcript
        fields = '__all__'

class ContactInfoSerializer(serializers.ModelSerializer):
    """
    Serializer for the ContactInfo model.
    Converts ContactInfo model instances to JSON and validates input data.
    """
    class Meta:
        model = ContactInfo
        fields = '__all__'

class WorkExperienceSerializer(serializers.ModelSerializer):
    """
    Serializer for the WorkExperience model.
    Converts WorkExperience model instances to JSON and validates input data.
    """
    class Meta:
        model = WorkExperience
        fields = '__all__'

class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for the UserProfile model.
    Converts UserProfile model instances to JSON and validates input data.
    """
    class Meta:
        model = UserProfile
        fields = '__all__'

class LanguageSerializer(serializers.ModelSerializer):
    """
    Serializer for the Language model.
    Converts Language model instances to JSON and validates input data.
    """
    class Meta:
        model = Language
        fields = '__all__'

class UserLanguageSerializer(serializers.ModelSerializer):
    """
    Serializer for the UserLanguage model.
    Converts UserLanguage model instances to JSON and validates input data.
    """
    class Meta:
        model = UserLanguage
        fields = '__all__'

class ResumeAnalysisSerializer(serializers.ModelSerializer):
    """
    Serializer for the ResumeAnalysis model.
    Converts ResumeAnalysis model instances to JSON and validates input data.
    """
    class Meta:
        model = ResumeAnalysis
        fields = '__all__'

class ProfileViewSerializer(serializers.ModelSerializer):
    """
    Serializer for the ProfileView model.
    Converts ProfileView model instances to JSON and validates input data.
    """
    class Meta:
        model = ProfileView
        fields = '__all__'
