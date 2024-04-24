
# ChatProject>ChatApp>consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
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
        # Set the user information in the scope during connection
        await self.set_user_in_scope()

    async def set_user_in_scope(self):
        user = self.scope.get('user', None)
        if user and user.is_authenticated:
            self.user = user
        else:
            self.user = AnonymousUser()

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        username = data['username']
        connection_type = data['type']
        print(connection_type)
        await self.change_online_status(username, connection_type)
        # Do not call update_active_users here

    async def disconnect(self, close_code):
        print("WebSocket disconnected.")
        # Remove user from room group
        if self.user:
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
            await self.set_user_inactive(self.user, self.room_group_name)


    @database_sync_to_async   
    def set_user_inactive(self, user, room_name):
        if user:
            try:
                connected_instance = Connected.objects.get(user=user, room_name=room_name)
                connected_instance.is_active = False
                connected_instance.last_activity = timezone.now()
                connected_instance.save()

                # Update user's online status in the UserProfileModel
                UserProfileModel.objects.filter(user=user).update(online_status=False)
            except Connected.DoesNotExist:
                print(f"Connected instance for user {user.username} in room {room_name} does not exist.")
            except Exception as e:
                print(f"Error updating user status: {e}")

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
            userprofile, _ = UserProfileModel.objects.get_or_create(user=user)
            userprofile.online_status = (c_type == 'open')
            userprofile.save()
        except User.DoesNotExist:
            print(f"User with username '{username}' does not exist.")
        except Exception as e:
            print(f"Error changing online status: {e}")

    def update_active_users(self):
        active_users = self.get_active_users()
        # Send updated active users list to the group
        self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'send_active_users',
                'active_users': active_users,
            }
        )