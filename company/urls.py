from django.urls import path
from . import views
 
urlpatterns = [
    path('update-company/', views.update_company, name="update-company"),
    path('company-details/<int:pk>',views.company_details,name="company-details"),
    path('company/<int:company_id>/applications/', views.view_applications, name='view_applications'),
    path('create_company/', views.create_company, name='create_company'),

]