from django.urls import path
from . import views
app_name = 'job'


urlpatterns = [
    path('create-job',views.create_job, name="create-job"),
    path('update-job/<int:pk>/',views.update_job, name="update-job"),
    path('apply/<int:job_id>/', views.apply_job, name='apply_job'),
    #Compiler path
    path('run-code/', views.run_code, name='run_code'),

]
