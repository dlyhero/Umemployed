from django.urls import path

from .views import (
    BulkDeleteMessagesAPIView,
    ChatMessageListAPIView,
    ConversationListAPIView,
    DeleteConversationAPIView,
    DeleteMessageAPIView,
    MarkMessagesAsReadAPIView,
    MessageReactionAPIView,
    SearchInboxAPIView,
    StartConversationAPIView,
    UpdateMessageAPIView,
)

urlpatterns = [
    path("conversations/", ConversationListAPIView.as_view(), name="conversation_list"),
    path(
        "conversations/<int:conversation_id>/messages/",
        ChatMessageListAPIView.as_view(),
        name="chat_message_list",
    ),
    path("conversations/start/", StartConversationAPIView.as_view(), name="start_conversation"),
    path("search-inbox/", SearchInboxAPIView.as_view(), name="search_inbox"),
    path(
        "conversations/<int:conversation_id>/mark-read/",
        MarkMessagesAsReadAPIView.as_view(),
        name="mark_messages_as_read",
    ),
    path(
        "conversations/<int:conversation_id>/delete/",
        DeleteConversationAPIView.as_view(),
        name="delete_conversation",
    ),
    path(
        "messages/<int:message_id>/reactions/",
        MessageReactionAPIView.as_view(),
        name="message_reaction",
    ),
    path(
        "messages/<int:message_id>/update/", UpdateMessageAPIView.as_view(), name="update_message"
    ),
    path(
        "messages/<int:message_id>/delete/", DeleteMessageAPIView.as_view(), name="delete_message"
    ),
    path(
        "conversations/<int:conversation_id>/bulk-delete/",
        BulkDeleteMessagesAPIView.as_view(),
        name="bulk_delete_messages",
    ),
]
