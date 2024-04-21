# ChatProject>ChatApp>consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from ChatApp.models import *
from django.utils import timezone

class ChatConsumer(AsyncWebsocketConsumer):
    # connect method
    async def connect(self):
        # Get room_name from URL or wherever it's stored
        room_name = self.scope['url_route']['kwargs']['room_name']
        # Assuming username is also available in self.scope
        username = self.scope['user'].username
        # Mark user as active
        Connected.set_user_active(self.scope['user'], room_name, is_active=True)
        # Accept connection
        self.accept()

        # self.room_name = f"room_{self.scope['url_route']['kwargs']['room_name']}"
        # await self.channel_layer.group_add(self.room_name, self.channel_name)
        # await self.accept()
    
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

    async def send_onlineStatus(self, event):
        data = json.loads(event.get('value'))
        username = data['username']
        online_status = data['status']
        await self.send(text_data=json.dumps({
            'username':username,
            'online_status':online_status
        }))


    async def disconnect(self, message):
        # Get room_name from URL or wherever it's stored
        room_name = self.scope['url_route']['kwargs']['room_name']
        # Mark user as inactive
        Connected.set_user_active(self.scope['user'], room_name, is_active=False)
        # self.channel_layer.group_discard(
        #     self.room_group_name,
        #     self.channel_name
        # )

    @database_sync_to_async
    def change_online_status(self, username, c_type):
        user = User.objects.get(username=username)
        userprofile = UserProfileModel.objects.get(user=user)
        if c_type == 'open':
            userprofile.online_status = True
            userprofile.save()
        else:
            userprofile.online_status = False
            userprofile.save()
