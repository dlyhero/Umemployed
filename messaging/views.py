from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Conversation, ChatMessage

User = get_user_model()

@login_required
def start_chat(request, user_id):
    selected_user = get_object_or_404(User, id=user_id)
    
    # Check if a conversation already exists between the two users
    conversation, created = Conversation.objects.get_or_create(
        participant1=request.user,
        participant2=selected_user
    )
    
    # If the conversation already exists, redirect to it
    return redirect('messaging:chat', conversation_id=conversation.id)

@login_required
def inbox_view(request):
    # Get existing chat rooms
    rooms = Conversation.objects.filter(participant1=request.user) | Conversation.objects.filter(participant2=request.user)
    
    # Get all users except the current user
    users = User.objects.exclude(id=request.user.id)
    
    if request.method == 'POST':
        # Handle the creation of new chat rooms
        selected_user_id = request.POST.get('selected_user')
        if selected_user_id:
            selected_user = User.objects.get(id=selected_user_id)
            
            # Check if a conversation already exists between the two users
            conversation, created = Conversation.objects.get_or_create(
                participant1=request.user,
                participant2=selected_user
            )
            
            if created:
                # Redirect to the chat view if the conversation was created successfully
                return redirect('messaging:chat', conversation_id=conversation.id)
            else:
                # If the conversation already exists, redirect to it
                return redirect('messaging:chat', conversation_id=conversation.id)
    
    context = {
        'rooms': rooms,
        'users': users
    }
    return render(request, 'inbox.html', context)
@login_required
def chat_view(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id)
    messagess = ChatMessage.objects.filter(conversation=conversation).order_by('timestamp')
    return render(request, 'chat.html', {'conversation': conversation, 'messagess': messagess})


from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .tasks import send_message_email_task

@login_required
def send_message(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id)
    if request.method == 'POST':
        text = request.POST.get('text')
        if text:
            message = ChatMessage.objects.create(conversation=conversation, sender=request.user, text=text)

            # Notify the recipient via WebSocket
            recipient = conversation.participant1 if conversation.participant2 == request.user else conversation.participant2
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'chat_{recipient.id}',
                {
                    'type': 'chat_message',
                    'message': message.text,
                    'sender': request.user.username,
                    'conversation_id': conversation.id
                }
            )

            # Send email notification
            send_message_email_task.delay(
                email=recipient.email,
                sender_name=request.user.get_full_name(),
                message_text=message.text,
                conversation_id=conversation.id
            )

        return redirect('messaging:chat', conversation_id=conversation_id)
    return redirect('messaging:chat', conversation_id=conversation_id)