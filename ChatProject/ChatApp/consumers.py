
# ChatProject>ChatApp>consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from ChatApp.models import *
from django.contrib.auth.models import User
from .models import UserProfileModel, Connected
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
# ChatProject>ChatApp>consumers.py

class OnlineStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'user'
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        username = data['username']
        connection_type = data['type']
        print(connection_type)
        await self.change_online_status(username, connection_type)
        # Do not call update_active_users here

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    @database_sync_to_async
    def set_user_active(user, room_name, is_active):
        Connected.objects.filter(user=user, room_name=room_name).update(
            is_active=is_active, 
            last_activity=timezone.now() if is_active else None
        )

    @database_sync_to_async
    def get_active_users(self):
        return list(UserProfileModel.objects.filter(online_status=True).values_list('user__username', flat=True))

    async def send_active_users(self, event):
        await self.send(text_data=json.dumps({
            'active_users': event['active_users']
        }))
        
    @database_sync_to_async
    def change_online_status(self, username, c_type):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # Handle the case where the user does not exist
            print(f"User with username '{username}' does not exist.")
            return
        
        userprofile, _ = UserProfileModel.objects.get_or_create(user=user)

        if c_type == 'open':
            userprofile.online_status = True
            userprofile.save()
        else:
            userprofile.online_status = False
            userprofile.save()
