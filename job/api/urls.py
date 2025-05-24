from django.urls import path
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.permissions import AllowAny
from . import views

app_name = 'job_api'

schema_view = get_schema_view(
    openapi.Info(
        title="Job API",
        default_version='v1',
        description="API documentation for the job application system",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="support@umemployed.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(AllowAny,),
)

urlpatterns = [
    # Swagger and Redoc documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # Job-related endpoints
    path('jobs/', views.JobListAPIView.as_view(), name='job_list'),  # List all available jobs
    path('jobs/<int:pk>/', views.JobDetailAPIView.as_view(), name='job_detail'),  # Retrieve job details
    path('jobs/<int:job_id>/apply/', views.ApplyJobAPIView.as_view(), name='apply_job'),  # Apply for a job
    path('jobs/<int:job_id>/save/', views.SaveJobAPIView.as_view(), name='save_job'),  # Save a job
    path('jobs/<int:job_id>/withdraw/', views.WithdrawApplicationAPIView.as_view(), name='withdraw_application'),  # Withdraw a job application
    path('jobs/<int:job_id>/shortlist/<int:candidate_id>/', views.ShortlistCandidateAPIView.as_view(), name='shortlist_candidate'),  # Shortlist a candidate
    path('jobs/<int:job_id>/decline/<int:candidate_id>/', views.DeclineCandidateAPIView.as_view(), name='decline_candidate'),  # Decline a candidate
    path('jobs/<int:job_id>/extracted-skills/', views.ExtractedSkillsAPIView.as_view(), name='extracted_skills'),  # Get extracted skills for a job
    path('jobs/<int:job_id>/tailored-description/', views.TailoredJobDescriptionAPIView.as_view(), name='tailored_job_description'),  # Get tailored job description

    # Saved jobs
    path('saved-jobs/', views.SavedJobsListAPIView.as_view(), name='saved_jobs'),  # List saved jobs

    # Question generation and skill extraction
    path('generate-questions/', views.GenerateQuestionsAPIView.as_view(), name='generate_questions'),  # Generate questions for skills
    path('extract-technical-skills/', views.ExtractTechnicalSkillsAPIView.as_view(), name='extract_technical_skills'),  # Extract technical skills from job description

    # Applied jobs
    path('applied-jobs/', views.AppliedJobsListAPIView.as_view(), name='applied_jobs'),  # List applied jobs

    # Job creation steps
    path('create-step1/', views.CreateJobStep1APIView.as_view(), name='create_job_step1'),  # Step 1: Create a job
    path('<int:job_id>/create-step2/', views.CreateJobStep2APIView.as_view(), name='create_job_step2'),  # Step 2: Update job preferences
    path('<int:job_id>/create-step3/', views.CreateJobStep3APIView.as_view(), name='create_job_step3'),  # Step 3: Update job description
    path('<int:job_id>/create-step4/', views.CreateJobStep4APIView.as_view(), name='create_job_step4'),  # Step 4: Update job requirements

    # Job options
    path('job-options/', views.JobOptionsAPIView.as_view(), name='job_options'),  # Fetch job-related options

    # Search jobs
    path('jobs/search/', views.SearchJobsAPIView.as_view(), name='search_jobs'),  # Search for jobs

    # Report test issues
    path('<int:job_id>/report-test/', views.ReportTestAPIView.as_view(), name='report_test_api'),  # Report test issues

    # Job questions
    path('<int:job_id>/questions/', views.JobQuestionsAPIView.as_view(), name='job_questions_api'),  # Fetch and submit job questions
]
