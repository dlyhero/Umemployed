from django.urls import path

from .views import MarkNotificationAsReadView, NotificationListView

urlpatterns = [
    path("notifications/", NotificationListView.as_view(), name="notification-list"),
    path(
        "notifications/<int:notification_id>/read/",
        MarkNotificationAsReadView.as_view(),
        name="mark-notification-as-read",
    ),
]
