from django.urls import path
from . import views

app_name = 'job_api'

urlpatterns = [
    path('jobs/', views.JobListAPIView.as_view(), name='job_list'),
    path('jobs/<int:pk>/', views.JobDetailAPIView.as_view(), name='job_detail'),
    path('jobs/<int:job_id>/apply/', views.ApplyJobAPIView.as_view(), name='apply_job'),
    path('jobs/<int:job_id>/save/', views.SaveJobAPIView.as_view(), name='save_job'),
    path('jobs/<int:job_id>/withdraw/', views.WithdrawApplicationAPIView.as_view(), name='withdraw_application'),
    path('jobs/<int:job_id>/shortlist/<int:candidate_id>/', views.ShortlistCandidateAPIView.as_view(), name='shortlist_candidate'),
    path('jobs/<int:job_id>/decline/<int:candidate_id>/', views.DeclineCandidateAPIView.as_view(), name='decline_candidate'),
    path('saved-jobs/', views.SavedJobsListAPIView.as_view(), name='saved_jobs'),
    path('generate-questions/', views.GenerateQuestionsAPIView.as_view(), name='generate_questions'),
    path('extract-technical-skills/', views.ExtractTechnicalSkillsAPIView.as_view(), name='extract_technical_skills'),
    path('applied-jobs/', views.AppliedJobsListAPIView.as_view(), name='applied_jobs'),
    path('create/', views.CreateJobAPIView.as_view(), name='create_job'),
    path('create-step1/', views.CreateJobStep1APIView.as_view(), name='create_job_step1'),
    path('<int:job_id>/create-step2/', views.CreateJobStep2APIView.as_view(), name='create_job_step2'),
    path('<int:job_id>/create-step3/', views.CreateJobStep3APIView.as_view(), name='create_job_step3'),
]
