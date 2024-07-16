from django.urls import path,include
from . import views

urlpatterns = [
    path('', views.dashboard,name='dashboard'),
    path('api/suggested-skills/', views.get_suggested_skills, name='get_suggested_skills'),
    path('update-user-skills/', views.update_user_skills, name='update_user_skills'),
    path('save-job/', views.save_job, name='save_job'),
    path('delete-skill/<int:skill_id>/', views.delete_skill, name='delete_skill'),
    path('paginated_skills/', views.paginated_skills, name='paginated_skills'),


]
