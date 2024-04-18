from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


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
    
class Connected(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="connected")
    room_name = models.CharField(max_length=100, null=False)
    channel_name = models.CharField(max_length=100, null=False)
    connect_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False) 

    def __str__(self):
        return str(self.user)