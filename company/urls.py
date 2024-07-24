from django.urls import path
from . import views
 
urlpatterns = [
    path('company/update/<uuid:company_id>/', views.update_company, name='update_company'),
    path('company-details/<uuid:company_id>',views.company_details,name="company-details"),
    path('<uuid:company_id>/applications/', views.view_applications, name='view_applications'),
    path('create_company/', views.create_company, name='create_company'),
    path('application/<uuid:company_id>/<uuid:application_id>/', views.view_application_details, name='view_application_details'),
    path('analytics/<uuid:company_id>/',views.company_analytics,name="company_analytics"),
    path('jobs/<uuid:company_id>/', views.view_my_jobs, name='view_my_jobs'),
    path('inbox/<uuid:company_id>/',views.company_inbox, name='company_inbox'),
    

]