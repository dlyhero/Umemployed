import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.conversation_id = self.scope["url_route"]["kwargs"]["conversation_id"]
        self.room_group_name = f"chat_{self.conversation_id}"

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        sender = self.scope["user"].username  # Get the sender's username

        # Save the message to the database
        await self.save_message(message, sender)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "sender": sender,  # Include the sender's information
            },
        )

    async def chat_message(self, event):
        message = event["message"]
        sender = event["sender"]  # Retrieve the sender's information

        # Send message to WebSocket
        await self.send(
            text_data=json.dumps(
                {
                    "message": message,
                    "sender": sender,  # Send the sender's information to the WebSocket
                }
            )
        )

    @database_sync_to_async
    def save_message(self, message, sender):
        from django.core.exceptions import ObjectDoesNotExist

        from messaging.models import ChatMessage, Conversation

        try:
            conversation = Conversation.objects.get(id=self.conversation_id)
            ChatMessage.objects.create(
                conversation=conversation, sender=self.scope["user"], text=message
            )
        except ObjectDoesNotExist:
            # Handle the case where the conversation does not exist
            pass
