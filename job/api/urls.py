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
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
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
    path('create-step1/', views.CreateJobStep1APIView.as_view(), name='create_job_step1'),
    path('<int:job_id>/create-step2/', views.CreateJobStep2APIView.as_view(), name='create_job_step2'),
    path('<int:job_id>/create-step3/', views.CreateJobStep3APIView.as_view(), name='create_job_step3'),
    path('<int:job_id>/create-step4/', views.CreateJobStep4APIView.as_view(), name='create_job_step4'),
]
