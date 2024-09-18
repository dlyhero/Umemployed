from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    # URL for viewing notifications
    path('', views.user_notifications, name='user_notifications'),

    # URL for marking a notification as read
    path('notifications/read/<int:notification_id>/', views.mark_notification_as_read, name='mark_notification_as_read'),
]