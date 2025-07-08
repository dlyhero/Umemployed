import logging

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


@shared_task
def send_message_email_task(email, sender_name, message_text, conversation_id):
    subject = f"New Message from {sender_name}"
    message = f"You have received a new message from {sender_name}:\n\n{message_text}\n\nView the conversation: {settings.SITE_URL}/messaging/chat/{conversation_id}/"
    from_email = settings.DEFAULT_FROM_EMAIL

    try:
        send_mail(subject, message, from_email, [email])
    except Exception as e:
        logger.error(f"An error occurred while sending email to {email}: {e}")
