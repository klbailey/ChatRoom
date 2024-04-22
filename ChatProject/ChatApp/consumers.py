# ChatProject>ChatApp>consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from ChatApp.models import *
from django.contrib.auth.models import User
from .models import UserProfileModel
from django.utils import timezone

class ChatConsumer(AsyncWebsocketConsumer):
    # connect method    
    async def connect(self):      
        self.room_name = f"room_{self.scope['url_route']['kwargs']['room_name']}"
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()
    
    # receive method
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json
        # print(message)
        # dictionary type is name of method send_message; message in message = text_data_json
        event = {
            'type': 'send_message',
            'message': message,
        }
        #Group_send for every user in socket we send message for every user in this socket/group
        await self.channel_layer.group_send(self.room_name, event)
    
    # When message sent it will be sent to every other user in room
    async def send_message(self, event):

        data = event['message']
        await self.create_message(data=data)
        # Ensure that the timestamp is included in the response_data
        response_data = {
            'sender': data['sender'],
            'message': data['message'],
            'timestamp': data['timestamp'] 
        }
        await self.send(text_data=json.dumps({'message': response_data}))
    
    # if message user typed already been saved
    @database_sync_to_async
    def create_message(self, data):
        # Accessing timezone here
        get_room_by_name = Room.objects.get(room_name=data['room_name'])
        
        if not Message.objects.filter(message=data['message']).exists():
            new_message = Message(room=get_room_by_name, sender=data['sender'], message=data['message'])
            new_message.save()  


# Listen for events related to user connections, updates, disconnections & updates online_status
# Listen for events related to user connections, updates, disconnections & updates online_status
class OnlineStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'user'
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        await self.update_active_users()  # CHANGE: Call update_active_users when a user connects

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        username = data['username']
        connection_type = data['type']
        print(connection_type)
        await self.change_online_status(username, connection_type)
        await self.update_active_users()  # CHANGE: Call update_active_users whenever user status changes

    async def disconnect(self, message):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        await self.update_active_users()  # CHANGE: Call update_active_users when a user disconnects

    @database_sync_to_async
    def get_active_users(self):
        return list(UserProfileModel.objects.filter(online_status=True).values_list('user__username', flat=True))

    async def update_active_users(self):
        active_users = await self.get_active_users()
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'send_active_users',
                'active_users': active_users
            }
        )

    async def send_active_users(self, event):
        await self.send(text_data=json.dumps({
            'active_users': event['active_users']
        }))
        
    @database_sync_to_async
    def change_online_status(self, username, c_type):
        user = User.objects.get(username=username)
        userprofile, _ = UserProfileModel.objects.get_or_create(user=user)

        if c_type == 'open':
            userprofile.online_status = True
            userprofile.save()
        else:
            userprofile.online_status = False
            userprofile.save()