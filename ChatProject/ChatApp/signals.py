#ChatProject>ChatApp>signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import UserProfileModel, ChatNotification, Connected, Message
import json
# Import the Signal class
from django.dispatch import Signal
from django.utils import timezone
# Define the signal
send_entry_message = Signal()
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

# signal handler triggers when new notification instance is created/sends notification to group
# w/count of unread notifications for that user
@receiver(post_save, sender=ChatNotification)
def send_notification(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        notification_obj = ChatNotification.objects.filter(is_seen=False, user=instance.user).count()
        user_id = str(instance.user.id)
        data = {
            'count':notification_obj
        }

        async_to_sync(channel_layer.group_send)(
            user_id, {
                'type':'send_notification',
                'value':json.dumps(data)
            }
        )

# Signal handler triggered when a online_status field of UserProfileModel instance is updated
# sends updated online status of user to 'user' group
@receiver(post_save, sender=UserProfileModel)
def send_onlineStatus(sender, instance, created, **kwargs):
    if not created:
        channel_layer = get_channel_layer()
        user = instance.user.username
        user_status = instance.online_status
        room_name = instance.room_name

        data = {
            'username':user,
            'status':user_status,
            'room': room_name
        }
        async_to_sync(channel_layer.group_send)(
            room_name, {
                'type': 'update_online_status',
                'value': json.dumps(data)
            }
        )

# Signal handler triggered when a Connected instance is created or updated
# Sends updated online status of user to the group corresponding to the room
@receiver(post_save, sender=Connected)
def update_online_status(sender, instance, created, **kwargs):
    if not created:
        channel_layer = get_channel_layer()
        user = instance.user.username
        user_status = instance.is_active
        room_name = instance.room_name
        
        data = {
            'username': user,
            'status': user_status,
            'room': room_name
        }
        async_to_sync(channel_layer.group_send)(
            room_name, {
                'type': 'update_online_status',
                'value': json.dumps(data)
            }
        )

@receiver(post_save, sender=Message)
def send_entry_message(sender, instance, created, **kwargs):
    if created:
        if instance.sender == 'System' and 'has entered the chatroom' in instance.message:
            print("Entry message created:", instance.message)  # Debug print statement
            # Construct the entry message data
            entry_message_data = {
                'type': 'entry_message',
                'message': instance.message,
                'timestamp': instance.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            }

            # Send the entry message data to all clients in the relevant room
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                instance.room.room_name, {
                    'type': 'send_entry_message',
                    'data': json.dumps(entry_message_data)
                }
            )

# Define the signal
send_entry_message = Signal()

# Signal handler to send entry message
@receiver(send_entry_message)
def handle_entry_message(sender, instance, user, created, **kwargs):
    if created:
        # Construct the entry message data
        entry_message_data = {
            'type': 'entry_message',
            'message': f"{user.username} has entered the chatroom",
            'timestamp': instance.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }

        # Send the entry message data to all clients in the relevant room
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            instance.room_name, {
                'type': 'send_entry_message',
                'data': json.dumps(entry_message_data)
            }
        )

@receiver(post_save, sender=UserProfileModel)
def log_user_login(sender, instance, created, **kwargs):
    if created:
        username = instance.user.username 
        room_name = instance.room_name
        # user = instance.user.username
        entry_message = f"{username} has joined the room"  # Create entry message
        # Send entry message to all users in the room
        Connected.send_entry_message(room_name, entry_message)


    