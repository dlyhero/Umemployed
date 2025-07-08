from django.contrib.auth import get_user_model
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from messaging.models import ChatMessage, Conversation

from .serializers import ChatMessageSerializer, ConversationSerializer

User = get_user_model()


class ConversationListAPIView(APIView):
    """
    Endpoint to fetch all conversations for the authenticated user.

    Method: GET
    URL: /api/messaging/conversations/
    Response:
    - 200 OK: Returns a list of conversations.
    Example Response:
    [
        {
            "id": 1,
            "participant1": "user1",
            "participant2": "user2",
            "created_at": "2025-05-01T12:00:00Z"
        }
    ]
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        conversations = Conversation.objects.filter(
            participant1=request.user
        ) | Conversation.objects.filter(participant2=request.user)
        serializer = ConversationSerializer(conversations, many=True)
        return Response(serializer.data)


class ChatMessageListAPIView(APIView):
    """
    Endpoint to fetch and send messages in a specific conversation.

    Methods:
    - GET: Retrieve all messages in a conversation.
    - POST: Send a new message in a conversation.

    URL: /api/messaging/conversations/<conversation_id>/messages/
    Request Body (POST):
    {
        "text": "Hello!"
    }
    Response:
    - 200 OK (GET): Returns a list of messages.
    - 201 Created (POST): Confirms the message was sent successfully.
    Example Response (GET):
    [
        {
            "id": 1,
            "conversation": 1,
            "sender": "user1",
            "text": "Hello!",
            "timestamp": "2025-05-01T12:00:00Z"
        }
    ]
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, conversation_id):
        conversation = get_object_or_404(Conversation, id=conversation_id)
        if request.user not in [conversation.participant1, conversation.participant2]:
            return Response({"error": "Unauthorized"}, status=403)

        messages = ChatMessage.objects.filter(conversation=conversation).order_by("timestamp")
        serializer = ChatMessageSerializer(messages, many=True)
        return Response(serializer.data)

    def post(self, request, conversation_id):
        conversation = get_object_or_404(Conversation, id=conversation_id)
        if request.user not in [conversation.participant1, conversation.participant2]:
            return Response({"error": "Unauthorized"}, status=403)

        text = request.data.get("text", "").strip()
        if not text:
            return Response({"error": "Message text is required"}, status=400)

        try:
            message = ChatMessage.objects.create(
                conversation=conversation, sender=request.user, text=text
            )
            serializer = ChatMessageSerializer(message)
            return Response(serializer.data, status=201)
        except Exception as e:
            return Response({"error": "Failed to create message"}, status=500)


class StartConversationAPIView(APIView):
    """
    Endpoint to start a new conversation with another user.

    Method: POST
    URL: /api/messaging/conversations/start/
    Request Body:
    {
        "user_id": 2
    }
    Response:
    - 201 Created: Returns the ID of the created conversation.
    Example Response:
    {
        "conversation_id": 1
    }
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_id = request.data.get("user_id")
        if not user_id:
            return Response({"error": "User ID is required"}, status=400)

        try:
            other_user = get_object_or_404(User, id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        if other_user == request.user:
            return Response({"error": "Cannot start conversation with yourself"}, status=400)

        # Check if conversation already exists (in either direction)
        conversation = Conversation.objects.filter(
            Q(participant1=request.user, participant2=other_user) |
            Q(participant1=other_user, participant2=request.user)
        ).first()

        if not conversation:
            conversation = Conversation.objects.create(
                participant1=request.user, 
                participant2=other_user
            )

        return Response({"conversation_id": conversation.id}, status=201)


class SearchInboxAPIView(APIView):
    """
    Endpoint to search conversations by participant name.

    Method: GET
    URL: /api/messaging/search-inbox/
    Query Parameters:
    - query: The search term to filter conversations.
    Response:
    - 200 OK: Returns a list of matching conversations.
    Example Response:
    [
        {
            "id": 1,
            "participant1": "user1",
            "participant2": "user2",
            "created_at": "2025-05-01T12:00:00Z"
        }
    ]
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.query_params.get("query", "").strip()
        if not query:
            return Response({"error": "Search query is required."}, status=400)

        conversations = Conversation.objects.filter(
            (
                Q(participant1__username__icontains=query)
                | Q(participant2__username__icontains=query)
            )
            & (Q(participant1=request.user) | Q(participant2=request.user))
        )

        serializer = ConversationSerializer(conversations, many=True)
        return Response(serializer.data)


class MarkMessagesAsReadAPIView(APIView):
    """
    Endpoint to mark all unread messages in a conversation as read.

    Method: POST
    URL: /api/messaging/conversations/<conversation_id>/mark-read/
    Response:
    - 200 OK: Confirms that messages were marked as read.
    Example Response:
    {
        "message": "Messages marked as read."
    }
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, conversation_id):
        conversation = get_object_or_404(Conversation, id=conversation_id)
        if request.user not in [conversation.participant1, conversation.participant2]:
            return Response({"error": "Unauthorized"}, status=403)

        # Mark messages as read (excluding messages sent by the current user)
        ChatMessage.objects.filter(
            conversation=conversation, is_read=False
        ).exclude(sender=request.user).update(is_read=True)
        
        return Response({"message": "Messages marked as read."}, status=200)


class DeleteConversationAPIView(APIView):
    """
    Endpoint to delete a specific conversation.

    Method: DELETE
    URL: /api/messaging/conversations/<conversation_id>/delete/
    Response:
    - 200 OK: Confirms that the conversation was deleted.
    Example Response:
    {
        "message": "Conversation deleted successfully."
    }
    """

    permission_classes = [IsAuthenticated]

    def delete(self, request, conversation_id):
        conversation = get_object_or_404(Conversation, id=conversation_id)
        if request.user not in [conversation.participant1, conversation.participant2]:
            return Response({"error": "Unauthorized"}, status=403)

        conversation.delete()
        return Response({"message": "Conversation deleted successfully."}, status=200)


from messaging.models import MessageReaction


class MessageReactionAPIView(APIView):
    """
    Endpoint to add or remove a reaction to a message.

    Methods:
    - POST: Add a reaction to a message.
    - DELETE: Remove a reaction from a message.

    URL: /api/messaging/messages/<message_id>/reactions/
    Request Body (POST):
    {
        "reaction": "like"
    }
    Response:
    - 201 Created (POST): Confirms the reaction was added successfully.
    - 200 OK (DELETE): Confirms the reaction was removed successfully.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, message_id):
        message = get_object_or_404(ChatMessage, id=message_id)
        reaction = request.data.get("reaction", "").strip().lower()
        
        valid_reactions = ['like', 'love', 'laugh', 'wow', 'sad', 'angry']
        if not reaction or reaction not in valid_reactions:
            return Response({
                "error": f"Valid reactions are: {', '.join(valid_reactions)}"
            }, status=400)

        # Remove any existing reaction by this user on this message first
        MessageReaction.objects.filter(message=message, user=request.user).delete()
        
        # Add the new reaction
        reaction_obj = MessageReaction.objects.create(
            message=message, user=request.user, reaction=reaction
        )
        return Response({"message": "Reaction added successfully."}, status=201)

    def delete(self, request, message_id):
        message = get_object_or_404(ChatMessage, id=message_id)
        reaction = request.data.get("reaction", "").strip().lower()
        
        if not reaction:
            return Response({"error": "Reaction is required."}, status=400)

        reaction_obj = MessageReaction.objects.filter(
            message=message, user=request.user, reaction=reaction
        ).first()
        
        if reaction_obj:
            reaction_obj.delete()
            return Response({"message": "Reaction removed successfully."}, status=200)
        return Response({"error": "Reaction not found."}, status=404)


class UpdateMessageAPIView(APIView):
    """
    Endpoint to update a specific message.

    Method: PUT
    URL: /api/messaging/messages/<message_id>/update/
    Request Body:
    {
        "text": "Updated message text."
    }
    Response:
    - 200 OK: Confirms the message was updated successfully.
    """

    permission_classes = [IsAuthenticated]

    def put(self, request, message_id):
        message = get_object_or_404(ChatMessage, id=message_id, sender=request.user)
        new_text = request.data.get("text", "").strip()
        if not new_text:
            return Response({"error": "Message text is required."}, status=400)

        message.text = new_text
        message.save()
        
        serializer = ChatMessageSerializer(message)
        return Response(serializer.data, status=200)


class DeleteMessageAPIView(APIView):
    """
    Endpoint to delete a specific message.

    Method: DELETE
    URL: /api/messaging/messages/<message_id>/delete/
    Response:
    - 200 OK: Confirms the message was deleted successfully.
    """

    permission_classes = [IsAuthenticated]

    def delete(self, request, message_id):
        message = get_object_or_404(ChatMessage, id=message_id, sender=request.user)
        message.delete()
        return Response({"message": "Message deleted successfully."}, status=200)


class BulkDeleteMessagesAPIView(APIView):
    """
    Endpoint to delete multiple messages in a conversation.

    Method: POST
    URL: /api/messaging/conversations/<conversation_id>/bulk-delete/
    Request Body:
    {
        "message_ids": [1, 2, 3]
    }
    Response:
    - 200 OK: Confirms the messages were deleted successfully.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, conversation_id):
        conversation = get_object_or_404(Conversation, id=conversation_id)
        if request.user not in [conversation.participant1, conversation.participant2]:
            return Response({"error": "Unauthorized"}, status=403)

        message_ids = request.data.get("message_ids", [])
        if not message_ids:
            return Response({"error": "Message IDs are required."}, status=400)

        if not isinstance(message_ids, list):
            return Response({"error": "Message IDs must be a list."}, status=400)

        # Only allow users to delete their own messages
        deleted_count = ChatMessage.objects.filter(
            id__in=message_ids, 
            conversation=conversation,
            sender=request.user
        ).delete()[0]
        
        return Response({
            "message": f"{deleted_count} messages deleted successfully."
        }, status=200)
