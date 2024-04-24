
#ChatProject>ChatApp>models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class Room(models.Model):
    room_name = models.CharField(max_length=255)

    def __str__(self):
        return self.room_name
    
    def return_room_messages(self):
        return Message.objects.filter(room=self)
    
    def create_new_room_message(self, sender, message):
        new_message = Message(room=self, sender=sender, message=message)
        new_message.save()

class Message(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    sender = models.CharField(max_length=255)
    message = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return str(self.room)

class UserProfileModel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(blank=True, null=True, max_length=100)
    online_status = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

class Connected(models.Model): 
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="connected") 
    room_name = models.CharField(max_length=100, null=False)
    channel_name = models.CharField(max_length=100, null=False)
    connect_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)
    last_activity = models.DateTimeField(auto_now=True)  # New field to track last activity time

    def __str__(self):
        return str(self.user)   

    @classmethod
    def set_user_active(cls, user, room_name, is_active=True):
        connected_instance, created = cls.objects.get_or_create(
            user=user, 
            room_name=room_name,
            defaults={'channel_name': 'default', 'is_active': is_active}
        )
        if not created:
            connected_instance.is_active = is_active
            connected_instance.last_activity = timezone.now()
            connected_instance.save()

    # @classmethod
    # def set_user_active(cls, user, room_name, is_active=True):
    #     connected_instance, created = cls.objects.get_or_create(user=user, room_name=room_name, defaults={'channel_name': 'default'})
    #     connected_instance.is_active = is_active
    #     connected_instance.last_activity = timezone.now()  # Update last activity time
    #     connected_instance.save()
        
    #     UserProfileModel.objects.filter(user=user).update(online_status=is_active)

        
    #     user_profile, created = UserProfileModel.objects.get_or_create(user=user)
    #     user_profile.online_status = is_active
    #     user_profile.save()

    @classmethod
    def get_online_users(cls, room_name):
        threshold_time = timezone.now() - timedelta(minutes=1)
        online_users = cls.objects.filter(room_name=room_name, last_activity__gte=threshold_time, is_active=True)
        return online_users

class ChatNotification(models.Model):
    chat = models.ForeignKey(Message, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_seen = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username