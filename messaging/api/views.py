from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from messaging.models import Conversation, ChatMessage
from django.contrib.auth import get_user_model
from django.db.models import Q
from .serializers import ConversationSerializer, ChatMessageSerializer

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

        messages = ChatMessage.objects.filter(conversation=conversation).order_by('timestamp')
        serializer = ChatMessageSerializer(messages, many=True)
        return Response(serializer.data)

    def post(self, request, conversation_id):
        conversation = get_object_or_404(Conversation, id=conversation_id)
        if request.user not in [conversation.participant1, conversation.participant2]:
            return Response({"error": "Unauthorized"}, status=403)

        text = request.data.get('text')
        if not text:
            return Response({"error": "Message text is required"}, status=400)

        message = ChatMessage.objects.create(
            conversation=conversation, sender=request.user, text=text
        )
        return Response({"message": "Message sent successfully"}, status=201)

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
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({"error": "User ID is required"}, status=400)

        other_user = get_object_or_404(User, id=user_id)
        conversation, created = Conversation.objects.get_or_create(
            participant1=request.user, participant2=other_user
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
        query = request.query_params.get('query', '').strip()
        if not query:
            return Response({"error": "Search query is required."}, status=400)

        conversations = Conversation.objects.filter(
            (Q(participant1__username__icontains=query) | Q(participant2__username__icontains=query)) &
            (Q(participant1=request.user) | Q(participant2=request.user))
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

        ChatMessage.objects.filter(conversation=conversation, sender__ne=request.user, is_read=False).update(is_read=True)
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