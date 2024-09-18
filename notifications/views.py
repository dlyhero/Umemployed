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


def user_notifications(request):
    notifications = request.user.notification_set.filter(is_read=False)
    return render(request, 'dashboard/notifications.html', {'notifications': notifications})

from django.shortcuts import redirect, get_object_or_404

def mark_notification_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return redirect('notifications:user_notifications')