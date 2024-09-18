# notifications/consumers.py

from channels.generic.websocket import AsyncWebsocketConsumer
import json

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # This is where you define the channel group to which this WebSocket will belong
        self.user_id = self.scope['user'].id
        self.group_name = f'notifications_{self.user_id}'

        # Join the WebSocket group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave the WebSocket group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def send_notification(self, event):
        # Send the notification to WebSocket
        notification = event['notification']
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'message': notification['message'],
            'notification_type': notification['notification_type']
        }))
