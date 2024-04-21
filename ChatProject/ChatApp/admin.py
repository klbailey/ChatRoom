#ChatProject>ChatApp>admin.py
from django.contrib import admin
from .models import *
from .models import Room, Message, Connected, UserProfileModel, ChatNotification

admin.site.register(Room)

class MessageAdmin(admin.ModelAdmin):
    list_display = ['room', 'sender', 'message']

admin.site.register(Message, MessageAdmin)
admin.site.register(UserProfileModel)
admin.site.register(Connected)
admin.site.register(ChatNotification)