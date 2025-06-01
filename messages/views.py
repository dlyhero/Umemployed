from django.shortcuts import render
from .models import *
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from notifications.models import Notification  # Add this import

# Create your views here.
@login_required(login_url="login")
def chats(request):
    user = request.user
    page = 'chats'
    messages = (Message.objects.filter(Q(sender = user) | Q(receiver = user)))
    # messages.sort(key = lambda  x: x.created, reverse=True)
    chats = {}
    for message in messages:
        if message.sender != user:
            try:
                chats.pop(message.sender)
                chats[message.sender]= message 
            except:
                chats[message.sender]= message
        else:
            try:
                chats[message.receiver]=message
                chats.pop(message.sender)
            except:
                chats[message.receiver]=message
    chats = [[key,value] for key,value in chats.items()]
    print(chats)
    chats.sort( key = lambda x : x[1].created, reverse=True)

    chats = dict(chats)


    context = { 'chats':chats,'page':page}
    return render(request, 'message/chats.html', context)


@login_required(login_url="login")
def chat(request, pk):
    user = User.objects.get(id = pk)
    if request.method == 'POST':
        text = request.POST.get('text')
        message = Message(text = text, sender = request.user, receiver = user)
        message.save()
        # Notify receiver of new message
        Notification.objects.create(
            user=user,
            notification_type=Notification.NEW_MESSAGE,
            message=f"You have received a new message from {request.user.get_full_name() or request.user.username}."
        )
    messages = list(Message.objects.filter(Q(sender = user, receiver = request.user) | Q(receiver = user, sender = request.user)))
    
    for message in messages:
        if message.sender != request.user:
            message.read = True
            message.save()
    
    room_name = Message.getRoomName(user, request.user)
    try:
        id = messages[-1].idd
    except:   

        id = 1
    
    context = {'messages':messages,'user':user, 'room_name':room_name,'id':id, 'me':request.user}
    return render(request, 'message/chat.html', context)
