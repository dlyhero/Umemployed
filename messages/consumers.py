import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from message.models import *
from datetime import datetime


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = f"room_{self.scope['url_route']['kwargs']['room_name']}"
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_name, self.channel_name)
    
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json
        event = {
            'type': 'send_message',
            'message': message
        }

        await self.channel_layer.group_send(self.room_name, event)

        print(message)
    

    
    async def send_message(self, event):
        data = event['message']
        
        id = await self.create_message(data= data)
        response = {
            'sender':data['sender'],
            'message':data['message'],
            'receiver':data['receiver'],
            'id':data['id'],
            'reply': data['reply'],
            'replytext': data['replytext'],
            'replyuser' : data['replyuser'],
            'msgid': id

        }
        await self.send(text_data = json.dumps({'message':response}))
    
    @database_sync_to_async
    def create_message(self, data):
        # get_room_name = Message.getRoomName(data['sender'], data['receiver'])
        
        if not Message.objects.filter(idd = data['id'], sender__id = data['sender'],receiver__id = data['receiver'] ).exists():
            
            sender = User.objects.get(id = data['sender'])
            receiver = User.objects.get(id = data['receiver'])
            idd = data['id']
            reply = None
            if data['reply']:
                reply = Message.objects.get(id = data['reply'])
            new_message = Message(text = data['message'], sender=sender, receiver = receiver, idd = idd, replyTo = reply)
            new_message.save()
            return new_message.id
            

            