from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

# Router for CRUD operations
router = DefaultRouter()
router.register(r'skills', views.SkillViewSet, basename='skills')  # CRUD for user skills
router.register(r'educations', views.EducationViewSet, basename='educations')  # CRUD for user education
router.register(r'experiences', views.ExperienceViewSet, basename='experiences')  # CRUD for user experiences
router.register(r'contact-info', views.ContactInfoViewSet, basename='contact_info')  # CRUD for user contact info
router.register(r'work-experiences', views.WorkExperienceViewSet, basename='work_experiences')  # CRUD for user work experiences
router.register(r'languages', views.LanguageViewSet, basename='languages')  # CRUD for user languages

# Additional endpoints for specific functionalities
urlpatterns = [
    path('update-resume/', views.update_resume_api, name='update_resume_api'),  # Update resume details
    path('resume-details/', views.resume_details_api, name='resume_details_api'),  # Get details of the latest resume
    path('matching-jobs/', views.matching_jobs_api, name='matching_jobs_api'),  # Get jobs matching the user's resume
    path('upload-resume/', views.upload_resume_api, name='upload_resume_api'),  # Upload and process a resume file
    path('analyze-resume/', views.analyze_resume_api, name='analyze_resume_api'),  # Analyze the uploaded resume
    path('upload-transcript/', views.upload_transcript_api, name='upload_transcript_api'),  # Upload and process a transcript
    path('extract-transcript/', views.extract_transcript_api, name='extract_transcript_api'),  # Extract text from a transcript
    path('resume-analysis/', views.resume_analysis_api, name='resume_analysis_api'),  # Analyze a resume file and provide feedback
    path('resume-analyses/', views.resume_analyses_api, name='resume_analyses_api'),  # Get all resume analyses for the user
    path('profile-views/', views.profile_views_api, name='profile_views_api'),  # Get all profile views for the user
]

# Include router URLs
urlpatterns += router.urls
