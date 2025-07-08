from django.urls import path

from . import views

app_name = "messaging"

urlpatterns = [
    path("inbox/", views.inbox_view, name="inbox"),
    path("chat/<int:conversation_id>/", views.chat_view, name="chat"),
    path("send_message/<int:conversation_id>/", views.send_message, name="send_message"),
    path("start_chat/<int:user_id>/", views.start_chat, name="start_chat"),  # New URL pattern
]
