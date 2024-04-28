#ChatProject>ChatApp>admin.py
from django.contrib import admin
from .models import Room, Message, Connected, UserProfileModel, ChatNotification

# Register your models with the admin site
admin.site.register(Room)
# admin.site.register(Message)
# admin.site.register(Connected) 
admin.site.register(UserProfileModel)
admin.site.register(ChatNotification)

class ConnectedAdmin(admin.ModelAdmin):
    list_display = ('user', 'room_name', 'channel_name', 'connect_date', 'is_active', 'last_activity')
    search_fields = ['user__username']  # Enable searching by username in the admin interface

admin.site.register(Connected, ConnectedAdmin)