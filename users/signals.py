import logging
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from django.db.models.signals import post_save

from users.email_tasks import send_welcome_email, send_login_email, send_logout_email, send_password_reset_email
from users.models import User

logger = logging.getLogger(__name__)

@receiver(post_save, sender=User)
def handle_user_registration(sender, instance, created, **kwargs):
    if created:
        logger.info('User registration signal triggered')
        send_welcome_email(instance.email, instance.first_name)

@receiver(user_logged_in)
def handle_user_login(sender, request, user, **kwargs):
    last_login = user.last_login
    now = timezone.now()
    if last_login and now - last_login > timedelta(days=30):  # 30 days as an example
        logger.info('User logged in after a long time')
        send_login_email(user.email, user.first_name)

# @receiver(user_logged_out)
# def handle_user_logout(sender, request, user, **kwargs):
#     logger.info('User logged out')
#     send_logout_email(user.email, user.first_name)

