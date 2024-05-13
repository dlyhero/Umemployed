from django.urls import path
from . import views
 
urlpatterns = [
    path('update-company/', views.update_company, name="update-company"),
    path('company-details/<int:pk>',views.company_details,name="company-details"),
    path('company/<uuid:company_id>/applications/', views.view_applications, name='view_applications'),
    path('create_company/', views.create_company, name='create_company'),
    path('application/<uuid:company_id>/<uuid:application_id>/', views.view_application_details, name='view_application_details'),
    path('analytics/<uuid:company_id>/',views.company_analytics,name="company_analytics")

]