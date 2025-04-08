from django.urls import path
from . import views

urlpatterns = [
    path('update-resume/', views.update_resume_api, name='update_resume_api'),
    path('resume-details/<int:pk>/', views.resume_details_api, name='resume_details_api'),
    path('matching-jobs/', views.matching_jobs_api, name='matching_jobs_api'),
    path('upload-resume/', views.upload_resume_api, name='upload_resume_api'),
    path('analyze-resume/', views.analyze_resume_api, name='analyze_resume_api'),
    path('upload-transcript/', views.upload_transcript_api, name='upload_transcript_api'),
    path('extract-transcript/', views.extract_transcript_api, name='extract_transcript_api'),
    path('resume-analysis/', views.resume_analysis_api, name='resume_analysis_api'),
    # Additional endpoints for serialized models
    path('skills/', views.skills_api, name='skills_api'),
    path('educations/', views.educations_api, name='educations_api'),
    path('experiences/', views.experiences_api, name='experiences_api'),
    path('contact-info/', views.contact_info_api, name='contact_info_api'),
    path('work-experiences/', views.work_experiences_api, name='work_experiences_api'),
    path('languages/', views.languages_api, name='languages_api'),
    path('resume-analyses/', views.resume_analyses_api, name='resume_analyses_api'),
    path('profile-views/', views.profile_views_api, name='profile_views_api'),
]
