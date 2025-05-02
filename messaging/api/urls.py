from django.urls import path
from .views import ConversationListAPIView, ChatMessageListAPIView, StartConversationAPIView, SearchInboxAPIView, MarkMessagesAsReadAPIView, DeleteConversationAPIView

urlpatterns = [
    path('conversations/', ConversationListAPIView.as_view(), name='conversation_list'),
    path('conversations/<int:conversation_id>/messages/', ChatMessageListAPIView.as_view(), name='chat_message_list'),
    path('conversations/start/', StartConversationAPIView.as_view(), name='start_conversation'),
    path('search-inbox/', SearchInboxAPIView.as_view(), name='search_inbox'),
    path('conversations/<int:conversation_id>/mark-read/', MarkMessagesAsReadAPIView.as_view(), name='mark_messages_as_read'),
    path('conversations/<int:conversation_id>/delete/', DeleteConversationAPIView.as_view(), name='delete_conversation'),
]