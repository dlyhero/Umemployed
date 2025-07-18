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
        fields = ["id", "user", "institution_name", "field_of_study", "degree", "graduation_year"]
        read_only_fields = ["id", "user"]
    
    def validate_graduation_year(self, value):
        """Validate graduation year is reasonable"""
        from datetime import datetime
        current_year = datetime.now().year
        
        if value < 1900 or value > current_year + 10:
            raise serializers.ValidationError(
                f"Graduation year must be between 1900 and {current_year + 10}"
            )
        return value


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
    
    skills = serializers.SerializerMethodField()
    profile_image_url = serializers.SerializerMethodField()
    cover_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Resume
        fields = "__all__"
    
    def get_skills(self, obj):
        """Return skills as objects with id and name"""
        return [{"id": skill.id, "name": skill.name} for skill in obj.skills.all()]
    
    def get_profile_image_url(self, obj):
        """Return profile image URL"""
        if obj.profile_image:
            return obj.profile_image.url
        return None
    
    def get_cover_image_url(self, obj):
        """Return cover image URL"""
        if obj.cover_image:
            return obj.cover_image.url
        return None


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

    firstName = serializers.SerializerMethodField()
    lastName = serializers.SerializerMethodField()
    bio = serializers.CharField(source="description", allow_blank=True, default="")
    description = serializers.CharField(allow_blank=True, default="")
    
    def get_firstName(self, obj):
        """Get user's first name"""
        return getattr(obj.user, 'first_name', '') or ''
    
    def get_lastName(self, obj):
        """Get user's last name"""
        return getattr(obj.user, 'last_name', '') or ''

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
    address = serializers.CharField(allow_blank=True, default="")  # Separate address field
    city = serializers.CharField(allow_blank=True, default="")  # Separate city field
    state = serializers.CharField(source="state", allow_blank=True, default="")  # State field
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
                "state": data.get("state") or "",
                "country": data.get("country") or "",
                "postalCode": data.get("postalCode") or "",
                "mobile": data.get("mobile") or "",
                "jobTitle": data.get("jobTitle") or "",
            }
        }


class ExperienceListSerializer(serializers.Serializer):
    """
    Serializer for user's experiences list for frontend.
    """
    def to_representation(self, instance):
        """Custom representation to handle the experiences structure"""
        # Get all experiences for the user
        experiences = Experience.objects.filter(user=instance.user).order_by('-start_date')
        
        experiences_data = []
        for exp in experiences:
            # Calculate period from start_date and end_date
            period = ""
            if exp.start_date:
                start_year = exp.start_date.year
                if exp.end_date:
                    end_year = exp.end_date.year
                    period = f"{start_year}-{str(end_year)[2:]}"  # e.g., "2019-22"
                else:
                    period = f"{start_year}-Present"
            
            experiences_data.append({
                "id": exp.id,
                "period": period,
                "logo": "/assets/default-company-logo.png",  # Default logo, can be customized
                "title": exp.role or "",
                "company": exp.company_name or "",
                "description": f"Worked as {exp.role} at {exp.company_name}" if exp.role and exp.company_name else ""
            })
        
        return {
            "experiences": experiences_data
        }


class EducationListSerializer(serializers.Serializer):
    """
    Serializer for user's education list for frontend.
    """
    def to_representation(self, instance):
        """Custom representation to handle the education structure"""
        # Get all education records for the user
        educations = Education.objects.filter(user=instance.user).order_by('-graduation_year')
        
        education_data = []
        for edu in educations:
            # Calculate period - assuming 4 years for bachelor's, 2 for diploma, etc.
            period = ""
            if edu.graduation_year:
                # Estimate start year based on degree type
                duration = 4  # Default duration
                if 'diploma' in edu.degree.lower() or 'high school' in edu.degree.lower():
                    duration = 2
                elif 'master' in edu.degree.lower():
                    duration = 2
                elif 'phd' in edu.degree.lower() or 'doctorate' in edu.degree.lower():
                    duration = 4
                
                start_year = edu.graduation_year - duration
                period = f"{start_year}-{str(edu.graduation_year)[2:]}"  # e.g., "2013-17"
            
            education_data.append({
                "id": edu.id,
                "period": period,
                "degree": edu.degree or "",
                "university": edu.institution_name or "",
                "description": f"Specialized in {edu.field_of_study}" if edu.field_of_study else ""
            })
        
        return {
            "education": education_data
        }


class SkillsListSerializer(serializers.Serializer):
    """
    Serializer for user's skills list for frontend.
    """
    def to_representation(self, instance):
        """Custom representation to handle the skills structure"""
        # Get all skills for the user
        skills = Skill.objects.filter(user=instance.user).order_by('name')
        
        skills_data = []
        for skill in skills:
            skills_data.append({
                "id": skill.id,
                "name": skill.name
            })
        
        return {
            "skills": skills_data
        }
