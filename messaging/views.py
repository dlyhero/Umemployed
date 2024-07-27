from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Message

@login_required
def inbox(request):
    user = request.user
    messages = Message.objects.filter(recipient=user)
    if user.is_recruiter:
        return render(request, 'messaging/recruiter_inbox.html', {'messages': messages})
    else:
        return render(request, 'messaging/applicant_inbox.html', {'messages': messages})

@login_required
def message_detail(request, message_id):
    message = get_object_or_404(Message, id=message_id, recipient=request.user)
    if request.user.is_recruiter:
        return render(request, 'messaging/recruiter_message_detail.html', {'message': message})
    else:
        return render(request, 'messaging/applicant_message_detail.html', {'message': message})
