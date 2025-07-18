from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views
from .views import AboutAPIView, CountriesAPIView, EducationAPIView, ExperiencesAPIView, PersonalDetailsAPIView, SkillsAPIView, UserLocationAPIView, UserImagesAPIView, SkillCategoriesAPIView, SimpleSkillsAPIView, JobCategoryStatusAPIView

# Router for CRUD operations
router = DefaultRouter()
router.register(r"skills", views.SkillViewSet, basename="skills")  # CRUD for user skills
router.register(
    r"educations", views.EducationViewSet, basename="educations"
)  # CRUD for user education
router.register(
    r"experiences", views.ExperienceViewSet, basename="experiences"
)  # CRUD for user experiences
router.register(
    r"contact-info", views.ContactInfoViewSet, basename="contact_info"
)  # CRUD for user contact info
router.register(
    r"work-experiences", views.WorkExperienceViewSet, basename="work_experiences"
)  # CRUD for user work experiences
router.register(
    r"languages", views.LanguageViewSet, basename="languages"
)  # CRUD for user languages

# Additional endpoints for specific functionalities
urlpatterns = [
    path(
        "update-resume/", views.update_resume_api, name="update_resume_api"
    ),  # Update resume details
    path(
        "resume-details/", views.resume_details_api, name="resume_details_api"
    ),  # Get details of the latest resume
    path(
        "matching-jobs/", views.matching_jobs_api, name="matching_jobs_api"
    ),  # Get jobs matching the user's resume
    path(
        "upload-resume/", views.upload_resume_api, name="upload_resume_api"
    ),  # Upload and process a resume file
    path(
        "analyze-resume/", views.analyze_resume_api, name="analyze_resume_api"
    ),  # Analyze the uploaded resume
    path(
        "upload-transcript/", views.upload_transcript_api, name="upload_transcript_api"
    ),  # Upload and process a transcript
    path(
        "extract-transcript/", views.extract_transcript_api, name="extract_transcript_api"
    ),  # Extract text from a transcript
    path(
        "resume-analysis/", views.resume_analysis_api, name="resume_analysis_api"
    ),  # Analyze a resume file and provide feedback
    path(
        "resume-analyses/", views.resume_analyses_api, name="resume_analyses_api"
    ),  # Get all resume analyses for the user
    path(
        "profile-views/", views.profile_views_api, name="profile_views_api"
    ),  # Get all profile views for the user
    path(
        "enhance-resume/<int:job_id>/", views.enhance_resume_api, name="enhance_resume_api"
    ),  # Enhance resume for a job with job_id in URL
    path(
        "enhancement-status/<str:task_id>/",
        views.resume_enhancement_status,
        name="resume_enhancement_status",
    ),  # Check status of resume enhancement task
    path(
        "skills-list/", views.SkillListView.as_view(), name="skill_list"
    ),  # Fetch all skills (id and name)
    path(
        "update-resume-fields/", views.update_resume_fields_api, name="update_resume_fields_api"
    ),  # Dedicated endpoint for updating Resume fields
    path(
        "enhancement-history/", views.enhancement_history_api, name="enhancement_history_api"
    ),  # Fetch user's enhanced resumes
    path(
        "check-enhanced-resume/<int:user_id>/<int:job_id>/",
        views.check_enhanced_resume_api,
        name="check_enhanced_resume_api",
    ),  # Check if the resume is enhanced for a specific job
    path(
        "user-profile/<int:user_id>/", 
        views.user_profile_details_api, 
        name="user_profile_details_api"
    ),  # Fetch user profile details by user ID
    
    # New endpoints for frontend
    path(
        "countries/",
        views.CountriesAPIView.as_view(),
        name="countries_api",
    ),  # GET list of countries for dropdown
    path(
        "skill-categories/",
        views.SkillCategoryListView.as_view(),
        name="skill_categories_api",
    ),  # GET list of job titles/skill categories for dropdown
    path(
        "skill-categories-optimized/",
        views.SkillCategoriesAPIView.as_view(),
        name="skill_categories_optimized_api",
    ),  # GET optimized skill categories with stats
    path(
        "states/",
        views.StatesAPIView.as_view(),
        name="states_api",
    ),  # GET list of US states for dropdown
    path(
        "about/",
        views.AboutAPIView.as_view(),
        name="about_api",
    ),  # GET/PUT/PATCH user's about information
    path(
        "personal-details/",
        views.PersonalDetailsAPIView.as_view(),
        name="personal_details_api",
    ),  # GET/PUT/PATCH user's personal details
    path(
        "user-location/",
        views.UserLocationAPIView.as_view(),
        name="user_location_api",
    ),  # GET/POST/PATCH user's country and city
    path(
        "user-images/",
        views.UserImagesAPIView.as_view(),
        name="user_images_api",
    ),  # GET/POST/DELETE user's profile and cover images
    path(
        "experiences/",
        views.ExperiencesAPIView.as_view(),
        name="experiences_api",
    ),  # GET/POST user's experiences list
    path(
        "education/",
        views.EducationAPIView.as_view(),
        name="education_api",
    ),  # GET/POST user's education list
    path(
        "skills/",
        views.SkillsAPIView.as_view(),
        name="skills_api",
    ),  # GET/POST/DELETE user's skills with pagination
    path(
        "skills-simple/",
        views.SimpleSkillsAPIView.as_view(),
        name="skills_simple_api",
    ),  # GET simple skills (job_relevant/user_only only)
    path(
        "job-category-status/",
        views.JobCategoryStatusAPIView.as_view(),
        name="job_category_status_api",
    ),  # GET/POST check and sync job title with category
    path(
        "languages-list/",
        views.LanguageListView.as_view(),
        name="languages_list_api",
    ),  # GET list of all available languages for dropdown
    path(
        "proficiency-levels/",
        views.ProficiencyChoicesAPIView.as_view(),
        name="proficiency_levels_api",
    ),  # GET list of all proficiency levels for dropdown
    path("user-stats/", views.UserStatsAPIView.as_view(), name="user-stats"),
]

# Include router URLs
urlpatterns += router.urls
