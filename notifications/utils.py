# notifications/utils.py

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Notification

def notify_user(user, message, notification_type=None):
    """
    Create a notification for the user and send it via WebSocket.
    
    :param user: The user to notify
    :param message: The message to display in the notification
    :param notification_type: (Optional) The type of event that triggered the notification
    """
    # Create the notification in the database
    Notification.objects.create(user=user, message=message, notification_type=notification_type)

    # Send the notification via WebSocket
    channel_layer = get_channel_layer()
    if channel_layer:
        async_to_sync(channel_layer.group_send)(
            f"notifications_{user.id}",
            {
                'type': 'send_notification',
                'notification': {
                    'message': message,
                    'notification_type': notification_type,
                }
            }
        )
