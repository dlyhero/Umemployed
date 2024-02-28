from django.urls import path 
from . import views 

urlpatterns = [
    path('update-resume/', views.update_resume, name='update-resume'),
    path('resume-details/<int:pk>/', views.resume_details, name='resume-details'),
    # path('onboarding-2/', views.applicant_onboarding_part2, name='onboarding-2'),
    path('onboarding-3/', views.applicant_onboarding_part3, name='onboarding-3'),
    path('matching-jobs/', views.display_matching_jobs, name='matching_jobs'),
    path('select-category/', views.select_category, name='select_category'),
    path('select-skills/', views.select_skills, name='select_skills'),
    # path('job/apply/<int:job_id>/', apply_job, name='apply_job'),
]
