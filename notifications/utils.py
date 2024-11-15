# notifications/utils.py

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Notification

def notify_user(user, message, notification_type=None):
    """
    Create a notification for the user and send it via WebSocket.
    
    :param user: The user to notify
    :param message: The message to display in the notification
    :param notification_type: The type of event that triggered the notification (should be one of the choices).
    """
    if notification_type is None:
        notification_type = Notification.ACCOUNT_ALERT  # Use a default value if none provided
    
    # Check that the notification_type is valid
    if notification_type not in dict(Notification.NOTIFICATION_TYPES):
        raise ValueError(f"Invalid notification type: {notification_type}")
    
    # Create the notification in the database
    Notification.objects.create(user=user, message=message, notification_type=notification_type)

    # Send the notification via WebSocket (if applicable)
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

