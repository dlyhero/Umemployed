from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .models import ChatMessage, Conversation

User = get_user_model()


@login_required
def start_chat(request, user_id):
    selected_user = get_object_or_404(User, id=user_id)

    # Check if a conversation already exists between the two users
    conversation, created = Conversation.objects.get_or_create(
        participant1=request.user, participant2=selected_user
    )

    # If the conversation already exists, redirect to it
    return redirect("messaging:chat", conversation_id=conversation.id)


@login_required
def inbox_view(request):
    # Get existing chat rooms
    rooms = Conversation.objects.filter(participant1=request.user) | Conversation.objects.filter(
        participant2=request.user
    )

    # Get all users except the current user
    users = User.objects.exclude(id=request.user.id)

    if request.method == "POST":
        # Handle the creation of new chat rooms
        selected_user_id = request.POST.get("selected_user")
        if selected_user_id:
            selected_user = User.objects.get(id=selected_user_id)

            # Check if a conversation already exists between the two users
            conversation, created = Conversation.objects.get_or_create(
                participant1=request.user, participant2=selected_user
            )

            if created:
                # Redirect to the chat view if the conversation was created successfully
                return redirect("messaging:chat", conversation_id=conversation.id)
            else:
                # If the conversation already exists, redirect to it
                return redirect("messaging:chat", conversation_id=conversation.id)

    context = {"rooms": rooms, "users": users}
    return render(request, "inbox.html", context)


from collections import defaultdict

from django.utils import timezone


@login_required
def chat_view(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id)
    messages = ChatMessage.objects.filter(conversation=conversation).order_by("timestamp")

    # Get existing chat rooms
    rooms = Conversation.objects.filter(participant1=request.user) | Conversation.objects.filter(
        participant2=request.user
    )

    # Get all users except the current user
    users = User.objects.exclude(id=request.user.id)

    # Determine the other user in the conversation
    if conversation.participant1 == request.user:
        other_user = conversation.participant2
    else:
        other_user = conversation.participant1

    # Group messages by date
    messages_by_date = defaultdict(list)
    for message in messages:
        message_date = message.timestamp.date()
        messages_by_date[message_date].append(message)

    context = {
        "conversation": conversation,
        "messages_by_date": dict(messages_by_date),
        "rooms": rooms,
        "users": users,
        "other_user": other_user,
    }
    return render(request, "chat.html", context)


from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .tasks import send_message_email_task


@login_required
def send_message(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id)
    if request.method == "POST":
        text = request.POST.get("text")
        if text:
            message = ChatMessage.objects.create(
                conversation=conversation, sender=request.user, text=text
            )

            # Notify the recipient via WebSocket
            recipient = (
                conversation.participant1
                if conversation.participant2 == request.user
                else conversation.participant2
            )
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"chat_{recipient.id}",
                {
                    "type": "chat_message",
                    "message": message.text,
                    "sender": request.user.username,
                    "conversation_id": conversation.id,
                },
            )

            # Send email notification
            send_message_email_task.delay(
                email=recipient.email,
                sender_name=request.user.get_full_name(),
                message_text=message.text,
                conversation_id=conversation.id,
            )

        return redirect("messaging:chat", conversation_id=conversation_id)
    return redirect("messaging:chat", conversation_id=conversation_id)
