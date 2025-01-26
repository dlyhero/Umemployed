from django.urls import path
from . import views
 
urlpatterns = [
    path('company/update/<int:company_id>/', views.update_company, name='update_company'),
    path('company-details/<int:company_id>/',views.company_details,name="company-details"),
    path('<int:company_id>/applications/', views.view_applications, name='view_applications'),
    path('create_company/', views.create_company, name='create_company'),
    path('application/<int:company_id>/<int:application_id>/', views.view_application_details, name='view_application_details'),
    path('analytics/<int:company_id>/',views.company_analytics,name="company_analytics"),
    path('jobs/<int:company_id>/', views.view_my_jobs, name='view_my_jobs'),
    path('inbox/<int:company_id>/',views.company_inbox, name='company_inbox'),
    path('notifications/<int:company_id>/',views.company_notifications, name='company_notifications'),
    path('dashboard/<int:company_id>/', views.company_dashboard, name="company_dashboard"),
    path('applications/<int:application_id>/details/', views.application_details, name='application_details'),
    path('company/<int:company_id>/job/<int:job_id>/applications/', views.job_applications_view, name='job_applications'),
    path('info/<int:pk>/', views.company_detail_view, name='company-detail'),
    path('<int:company_id>/jobs/', views.company_jobs_list_view, name='company-jobs-list'),
    path('companies/', views.company_list_view, name='company-list'),
    path('create_interview/', views.create_interview, name='create_interview'),  
    path('rate_candidate/<int:candidate_id>/', views.rate_candidate, name='rate_candidate'),
    path('related-users/', views.company_related_users, name='company_related_users'),





]