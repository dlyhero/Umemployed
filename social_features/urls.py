from django.urls import path

from . import views

urlpatterns = [
    path("create_post/", views.create_post, name="create_post"),
    path("post/<uuid:post_id>/", views.view_post, name="view_post"),
    path("post/<uuid:post_id>/edit/", views.edit_post, name="edit_post"),
    path("post/<uuid:post_id>/delete/", views.delete_post, name="delete_post"),
    path("send_message/<uuid:recipient_id>/", views.send_message, name="send_message"),
    path("message/<uuid:message_id>/", views.view_message, name="view_message"),
    path("message/<uuid:message_id>/delete/", views.delete_message, name="delete_message"),
    path("inbox/", views.inbox, name="inbox"),
]
