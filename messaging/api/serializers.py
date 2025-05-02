from rest_framework import serializers
from messaging.models import Conversation, ChatMessage

class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = ['id', 'participant1', 'participant2', 'created_at']

class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['id', 'conversation', 'sender', 'text', 'timestamp']