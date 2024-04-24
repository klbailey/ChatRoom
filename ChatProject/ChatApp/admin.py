#ChatProject>ChatApp>admin.py
from django.contrib import admin
from .models import Room, Message, Connected, UserProfileModel, ChatNotification

# Register your models with the admin site
admin.site.register(Room)
admin.site.register(Message)
admin.site.register(Connected)
admin.site.register(UserProfileModel)
admin.site.register(ChatNotification)
