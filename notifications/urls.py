from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.user_notifications, name='user_notifications'),
]
