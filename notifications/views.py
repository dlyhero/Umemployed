from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Notification

@login_required
def notifications(request):
    user = request.user
    notifications = Notification.objects.filter(user=user)
    if user.is_recruiter:
        return render(request, 'notifications/recruiter_notifications.html', {'notifications': notifications})
    else:
        return render(request, 'notifications/applicant_notifications.html', {'notifications': notifications})
