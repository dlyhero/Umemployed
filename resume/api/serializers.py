from rest_framework import serializers
from django_countries import countries

from resume.models import (
    ContactInfo,
    Education,
    EnhancedResume,
    Experience,
    Language,
    ProfileView,
    Resume,
    ResumeAnalysis,
    ResumeDoc,
    Skill,
    SkillCategory,
    Transcript,
    UserLanguage,
    UserProfile,
    WorkExperience,
)
from users.models import User


class CountriesSerializer(serializers.Serializer):
    """
    Serializer for countries dropdown list.
    """

    def to_representation(self, instance):
        """Return list of countries for dropdown"""
        return {
            "countries": [
                {"code": code, "name": name} for code, name in countries
            ]
        }


class SkillCategorySerializer(serializers.ModelSerializer):
    """
    Serializer for the SkillCategory model.
    Converts SkillCategory model instances to JSON and validates input data.
    """

    class Meta:
        model = SkillCategory
        fields = "__all__"


class SkillSerializer(serializers.ModelSerializer):
    """
    Serializer for the Skill model.
    Converts Skill model instances to JSON and validates input data.
    """

    class Meta:
        model = Skill
        fields = "__all__"


class SkillListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for SkillListView to optimize performance.
    Only includes essential fields for dropdowns and lists.
    """

    categories = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Skill
        fields = ["id", "name", "categories"]


class EducationSerializer(serializers.ModelSerializer):
    """
    Serializer for the Education model.
    Converts Education model instances to JSON and validates input data.
    """

    class Meta:
        model = Education
        fields = "__all__"


class ExperienceSerializer(serializers.ModelSerializer):
    """
    Serializer for the Experience model.
    Converts Experience model instances to JSON and validates input data.
    """

    class Meta:
        model = Experience
        fields = "__all__"


class ResumeSerializer(serializers.ModelSerializer):
    """
    Serializer for the Resume model.
    Converts Resume model instances to JSON and validates input data.
    """

    class Meta:
        model = Resume
        fields = "__all__"


class ResumeDocSerializer(serializers.ModelSerializer):
    """
    Serializer for the ResumeDoc model.
    Converts ResumeDoc model instances to JSON and validates input data.
    """

    class Meta:
        model = ResumeDoc
        fields = "__all__"


class TranscriptSerializer(serializers.ModelSerializer):
    """
    Serializer for the Transcript model.
    Converts Transcript model instances to JSON and validates input data.
    """

    class Meta:
        model = Transcript
        fields = "__all__"


class ContactInfoSerializer(serializers.ModelSerializer):
    """
    Serializer for the ContactInfo model.
    Converts ContactInfo model instances to JSON and validates input data.
    """

    job_title_name = serializers.StringRelatedField(source="job_title")  # Human-readable name
    job_title_id = serializers.PrimaryKeyRelatedField(
        queryset=SkillCategory.objects.all(), source="job_title"
    )  # Integer ID

    class Meta:
        model = ContactInfo
        fields = [
            "id",
            "name",
            "email",
            "phone",
            "country",
            "city",
            "date_of_birth",
            "job_title_name",
            "job_title_id",
        ]


class WorkExperienceSerializer(serializers.ModelSerializer):
    """
    Serializer for the WorkExperience model.
    Converts WorkExperience model instances to JSON and validates input data.
    """

    class Meta:
        model = WorkExperience
        fields = "__all__"


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for the UserProfile model.
    Converts UserProfile model instances to JSON and validates input data.
    """

    class Meta:
        model = UserProfile
        fields = "__all__"


class LanguageSerializer(serializers.ModelSerializer):
    """
    Serializer for the Language model.
    Converts Language model instances to JSON and validates input data.
    """

    class Meta:
        model = Language
        fields = ["id", "name"]


class UserLanguageSerializer(serializers.ModelSerializer):
    """
    Serializer for the UserLanguage model.
    Returns id, language (with id and name), and proficiency.
    """

    language = LanguageSerializer(read_only=True)
    language_id = serializers.PrimaryKeyRelatedField(
        queryset=Language.objects.all(), source="language", write_only=True, required=False
    )

    class Meta:
        model = UserLanguage
        fields = ["id", "language", "language_id", "proficiency"]


class ResumeAnalysisSerializer(serializers.ModelSerializer):
    """
    Serializer for the ResumeAnalysis model.
    Converts ResumeAnalysis model instances to JSON and validates input data.
    """

    class Meta:
        model = ResumeAnalysis
        fields = "__all__"


class ProfileViewSerializer(serializers.ModelSerializer):
    """
    Serializer for the ProfileView model.
    Converts ProfileView model instances to JSON and validates input data.
    """

    class Meta:
        model = ProfileView
        fields = "__all__"


class EnhancedResumeSerializer(serializers.ModelSerializer):
    """
    Serializer for the EnhancedResume model.
    Converts EnhancedResume model instances to JSON and validates input data.
    """

    class Meta:
        model = EnhancedResume
        fields = [
            "id",
            "user",
            "job",
            "full_name",
            "email",
            "phone",
            "linkedin",
            "location",
            "summary",
            "skills",
            "experience",
            "education",
            "certifications",
            "projects",
            "languages",
            "awards",
            "publications",
            "volunteer_experience",
            "interests",
            "created_at",
        ]


class AboutSerializer(serializers.Serializer):
    """
    Serializer for user's about information combining User and Resume models.
    """

    firstName = serializers.CharField(source="user.first_name", allow_blank=True, default="")
    lastName = serializers.CharField(source="user.last_name", allow_blank=True, default="")
    bio = serializers.CharField(source="description", allow_blank=True, default="")
    description = serializers.CharField(allow_blank=True, default="")

    def to_representation(self, instance):
        """Custom representation to handle the about structure"""
        data = super().to_representation(instance)
        return {
            "about": {
                "firstName": data.get("firstName") or "",
                "lastName": data.get("lastName") or "",
                "bio": data.get("bio") or "",
                "description": data.get("description") or "",
            }
        }


class PersonalDetailsSerializer(serializers.Serializer):
    """
    Serializer for user's personal details combining User and Resume models.
    """

    email = serializers.EmailField(source="user.email")
    dob = serializers.SerializerMethodField()
    address = serializers.CharField(source="state", allow_blank=True, default="")
    city = serializers.CharField(source="state", allow_blank=True, default="")  # Using state as city for now
    country = serializers.CharField(allow_blank=True, default="")
    postalCode = serializers.CharField(default="", allow_blank=True)  # Not in current model
    mobile = serializers.CharField(source="phone", allow_blank=True, default="")
    jobTitle = serializers.CharField(source="job_title", allow_blank=True, default="")

    def get_dob(self, obj):
        """Format date of birth as requested"""
        if obj.date_of_birth:
            return obj.date_of_birth.strftime("%dst %b, %Y").replace("1st", "1st").replace("2nd", "2nd").replace("3rd", "3rd").replace("st", "th")
        return ""

    def to_representation(self, instance):
        """Custom representation to handle the personalDetails structure"""
        data = super().to_representation(instance)
        return {
            "personalDetails": {
                "email": data.get("email") or "",
                "dob": data.get("dob") or "",
                "address": data.get("address") or "",
                "city": data.get("city") or "",
                "country": data.get("country") or "",
                "postalCode": data.get("postalCode") or "",
                "mobile": data.get("mobile") or "",
                "jobTitle": data.get("jobTitle") or "",
            }
        }
