from django.urls import path
from . import views

urlpatterns = [
    path('create-company/', views.CreateCompanyAPIView.as_view(), name='api_create_company'),
    path('update-company/<int:company_id>/', views.UpdateCompanyAPIView.as_view(), name='api_update_company'),
    path('company-details/<int:company_id>/', views.CompanyDetailsAPIView.as_view(), name='api_company_details'),
    path('list-companies/', views.CompanyListAPIView.as_view(), name='api_list_companies'),
    path('company/<int:company_id>/dashboard/', views.CompanyDashboardAPIView.as_view(), name='api_company_dashboard'),
    path('company/<int:company_id>/analytics/', views.CompanyAnalyticsAPIView.as_view(), name='api_company_analytics'),
    path('company/<int:company_id>/jobs/', views.ViewMyJobsAPIView.as_view(), name='api_view_my_jobs'),
    path('company/<int:company_id>/applications/', views.ViewApplicationsAPIView.as_view(), name='api_view_applications'),
    path('application/<int:application_id>/', views.ApplicationDetailsAPIView.as_view(), name='api_application_details'),
    path('company/<int:company_id>/job/<int:job_id>/applications/', views.JobApplicationsViewAPIView.as_view(), name='api_job_applications_view'),
    path('company/<int:company_id>/job/<int:job_id>/shortlisted/', views.ShortlistedCandidatesAPIView.as_view(), name='api_shortlisted_candidates'),
    path('company/<int:company_id>/job/<int:job_id>/shortlist/', views.ShortlistCandidateAPIView.as_view(), name='api_shortlist_candidate'),
    path('company/<int:company_id>/job/<int:job_id>/unshortlist/', views.UnshortlistCandidateAPIView.as_view(), name='api_unshortlist_candidate'),
    path('companies/', views.CompanyListAPIView.as_view(), name='api_company_list'),
    path('create-interview/', views.CreateInterviewAPIView.as_view(), name='api_create_interview'),
    path('rate-candidate/<int:candidate_id>/', views.RateCandidateAPIView.as_view(), name='api_rate_candidate'),
    path('related-users/', views.CompanyRelatedUsersAPIView.as_view(), name='api_company_related_users'),
    path('candidate/<int:candidate_id>/endorsements/', views.CandidateEndorsementsAPIView.as_view(), name='api_candidate_endorsements'),
    path('check-payment-status/<int:candidate_id>/', views.CheckPaymentStatusAPIView.as_view(), name='api_check_payment_status'),
    path('my-shortlisted-jobs/', views.MyShortlistedJobsAPIView.as_view(), name='api_my_shortlisted_jobs'),
]
