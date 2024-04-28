
# ChatProject>ChatApp>consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from ChatApp.models import *
from django.contrib.auth.models import User
from .models import UserProfileModel, Connected
from django.utils import timezone
from asgiref.sync import sync_to_async

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
        print("Data received:", data)
        print("Data structure:", type(data))
        print("Keys in data:", data.keys())
        if 'sender' not in data:
            print("Sender information missing in the received data.")
            return
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
        # Check if the message type is 'message'
        if data.get('type') == 'message' and 'message' in data:
            # Get the room by name
            try:
                room = Room.objects.get(room_name=data['room_name'])
            except Room.DoesNotExist:
                print("Room does not exist.")
                return
            
            # Check if the message already exists in the database
            if not Message.objects.filter(message=data['message']).exists():
                # Create and save the new message
                new_message = Message(room=room, sender=data['sender'], message=data['message'])
                new_message.save()
                print("Message saved successfully.")
            else:
                print("Message already exists.")
        else:
            print("Invalid message type or missing 'message' key in data.")

    
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
        username = data.get('username')
        connection_type = data.get('type')
        if username and connection_type:
            await self.change_online_status(username, connection_type)
        else:
            print("Invalid data format.")

    async def disconnect(self, close_code):
        print("WebSocket disconnected.")
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    @sync_to_async
    def change_online_status(self, username, c_type):
        try:
            user = User.objects.get(username=username)
            userprofile, _ = UserProfileModel.objects.get_or_create(user=user)
            userprofile.online_status = (c_type == 'open')
            userprofile.save()
        except User.DoesNotExist:
            print(f"User with username '{username}' does not exist.")
        except Exception as e:
            print(f"Error changing online status: {e}")