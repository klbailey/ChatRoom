
#ChatProject>ChatApp>signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import UserProfileModel, ChatNotification, Connected
import json

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

        data = {
            'username':user,
            'status':user_status
        }
        async_to_sync(channel_layer.group_send)(
            'user', {
                'type':'send_onlineStatus',
                'value':json.dumps(data)
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