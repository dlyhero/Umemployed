from django.urls import path 
from . import views 
from .extract_pdf import *
from .resume_analysis import resume_analysis, analyze_resume_view
from .transcript_job_title import upload_transcript,extract_transcript_text

# app_name = 'resume'

urlpatterns = [
    path('update-resume/', views.update_resume, name='update-resume'),
    path('resume/update/', views.update_resume_view, name='update_resume'),
    path('resume-details/<int:pk>/', views.resume_details, name='resume-details'),
    # path('onboarding-2/', views.applicant_onboarding_part2, name='onboarding-2'),
    path('onboarding-3/', views.applicant_onboarding_part3, name='onboarding-3'),
    path('matching-jobs/', views.display_matching_jobs, name='matching_jobs'),
    path('select-category/', views.select_category, name='select_category'),
    path('selec-skills/', views.selec_skills, name='selec_skill'),
    # path('job/apply/<int:job_id>/', apply_job, name='apply_job'),
    path('upload/', upload_resume, name='upload'),
    path('extract-text/<path:file_path>/', extract_text, name='extract_text'),
    path('extract-technical-skills/<path:file_path>/', extract_technical_skills, name='extract_technical_skills'),
    path('analyze-resume/', analyze_resume_view, name='analyze_resume'),
    path('resume-analysis/', resume_analysis, name='resume_analysis'),
    
    path('upload-transcript/', upload_transcript, name='upload_transcript'),
    path('extract-transcript/<path:file_path>/', extract_transcript_text, name='extract_transcript_text'),
]
