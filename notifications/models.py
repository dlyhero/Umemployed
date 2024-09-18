from django.db import models
from django.conf import settings

class Notification(models.Model):
    JOB_APPLICATION = 'job_application'
    NEW_JOB_POSTED = 'new_job_posted'
    ENDORSEMENT = 'endorsement'
    INTERVIEW_SCHEDULED = 'interview_scheduled'
    ACCOUNT_ALERT = 'account_alert'
    UPCOMING_EVENT = 'upcoming_event'
    NEW_MESSAGE = 'new_message'
    SPECIAL_OFFER = 'special_offer'
    PROFILE_UPDATED = 'profile_updated'

    NOTIFICATION_TYPES = [
        (JOB_APPLICATION, 'Job Application Received'),
        (NEW_JOB_POSTED, 'New Job Posted'),
        (ENDORSEMENT, 'Endorsement Received'),
        (INTERVIEW_SCHEDULED, 'Interview Scheduled'),
        (ACCOUNT_ALERT, 'Account Security Alert'),
        (UPCOMING_EVENT, 'Upcoming Event Reminder'),
        (NEW_MESSAGE, 'New Message Received'),
        (SPECIAL_OFFER, 'Special Offer'),
        (PROFILE_UPDATED, 'Profile Updated'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.get_notification_type_display()}: {self.message}"
