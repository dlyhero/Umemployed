from django.urls import path,include
from . import views

urlpatterns = [
    path('', views.dashboard,name='user_dashboard'),
    path('api/suggested-skills/', views.get_suggested_skills, name='get_suggested_skills'),
    path('update-user-skills/', views.update_user_skills, name='update_user_skills'),
    path('save-job/', views.save_job, name='save_job'),
    path('delete-skill/<int:skill_id>/', views.delete_skill, name='delete_skill'),
    path('paginated_skills/', views.paginated_skills, name='paginated_skills'),
    path('update_profile/', views.update_profile, name='update_profile'),
    path('delete_language/<int:language_id>/', views.delete_language, name='delete_language'),
    path('education/<int:id>/', views.get_education, name='get_education'),
    path('education/<int:id>/delete/', views.delete_education, name='delete_education'),
    path('education/save/', views.save_education, name='save_education'),
    
    path('experience/<int:id>/', views.get_experience_details, name='get_experience_details'),
    path('experience/<int:id>/delete/', views.delete_experience, name='delete_experience'),
    path('experience/save/', views.save_experience, name='save_experience'),


]
