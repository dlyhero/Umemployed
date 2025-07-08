from rest_framework import serializers

from messaging.models import ChatMessage, Conversation, MessageReaction


class ConversationSerializer(serializers.ModelSerializer):
    participant1_username = serializers.CharField(source='participant1.username', read_only=True)
    participant2_username = serializers.CharField(source='participant2.username', read_only=True)
    
    class Meta:
        model = Conversation
        fields = ["id", "participant1", "participant2", "participant1_username", "participant2_username", "created_at"]


class MessageReactionSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = MessageReaction
        fields = ["id", "user", "username", "reaction"]


class ChatMessageSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source='sender.username', read_only=True)
    reactions = MessageReactionSerializer(many=True, read_only=True)
    
    class Meta:
        model = ChatMessage
        fields = ["id", "conversation", "sender", "sender_username", "text", "timestamp", "is_read", "reactions"]
