from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Conversation, ChatMessage

User = get_user_model()

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
    return render(request, 'company/inbox.html', context)
@login_required
def chat_view(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id)
    messages = ChatMessage.objects.filter(conversation=conversation).order_by('timestamp')
    return render(request, 'chat.html', {'conversation': conversation, 'messages': messages})

@login_required
def send_message(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id)
    if request.method == 'POST':
        text = request.POST.get('text')
        if text:
            ChatMessage.objects.create(conversation=conversation, sender=request.user, text=text)
        return redirect('messaging:chat', conversation_id=conversation_id)
    return redirect('messaging:chat', conversation_id=conversation_id)
