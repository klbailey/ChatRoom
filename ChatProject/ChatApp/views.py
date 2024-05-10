
#ChatProject>ChatApp>views.py

from django.shortcuts import render, redirect
from .models import *
from django.http import HttpResponse
from .models import Connected, UserProfileModel
from django.contrib.auth import authenticate, login, logout
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from django.http import Http404, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from .models import Connected, UserProfileModel, Room
from django.contrib.auth.decorators import login_required
from .models import UserProfileModel, Room
from django.urls import reverse


from django.http import JsonResponse
# from django.contrib.auth.forms import UserCreationForm

def CreateRoom(request):
    if request.method == 'POST':
        username = request.POST['username']
        room = request.POST['room']
        # EITHER GET ROOM OBJECT OR CREATE IF IT DOESN'T EXIST
        try:
            get_room = Room.objects.get(room_name=room)
            
            return redirect('room', room_name=room, username=username)
        # IF THE ROOM DOES NOT EXIST, WE WILL CREATE IT AND SAVE
        except Room.DoesNotExist:
            new_room = Room(room_name = room)
            new_room.save()
            # SET USER AS ACTIVE IN SESSION
            request.session[f'room_{room}_{username}'] = True
            return redirect('room', room_name=room, username=username)
    rooms = Room.objects.all().values_list('room_name', flat=True)
    return render(request, 'index.html', {'rooms': rooms})

# @login_required
# def MessageView(request, room_name, username):
#     print("anything")
#     print("User:", username)

#     # Get or create a Connected instance for the user in the room request.user is always returning admin
#     connected_instance, created = Connected.objects.get_or_create(user=request.user, room_name=room_name, defaults={'channel_name': 'default'})
    
#     # Set user as active in the room
#     connected_instance.is_active = True
#     connected_instance.save()

#     # Update user's online status
#     UserProfileModel.objects.filter(user=request.user).update(online_status=True)
    
#     # Get room object by name
#     get_room = Room.objects.get(room_name=room_name)

#     # Get active users in the current room
#     active_users = list(Connected.objects.filter(room_name=room_name, is_active=True).exclude(user=request.user).values_list('user__username', flat=True))
    
#     # Add the current user to the active users list if not already present
#     if request.user.username not in active_users:
#         active_users.append(request.user.username)

#     # Debug output to check active_users
#     print("Active Users:", active_users)

#     if request.method == 'POST':
#         message = request.POST['message']
#         new_message = Message(room=get_room, sender=request.user.username, message=message)
        
#         new_message.save()

#     get_messages = Message.objects.filter(room=get_room)
    
#     context = {
#         "messages": get_messages,
#         "user": username,
#         "room_name": room_name,
#         "active_users": active_users,  # Pass active users to the template
#     }
#     return render(request, 'message.html', context)
 


@login_required
def MessageView(request, room_name, username):
    try:
        # Get the user object corresponding to the username from the URL
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        user = User.objects.create_user(username=username)

    # Get or create the UserProfileModel instance for the user
    user_profile, _ = UserProfileModel.objects.get_or_create(user=user)

    

    # If the user profile name is not set, set it to the username
    if not user_profile.name:
        user_profile.name = user.username
        user_profile.save()

    # Set the user as active in the room
    Connected.set_user_active(user, room_name, is_active=True)
    
    # Get the room object by name
    room = Room.objects.get(room_name=room_name)

    # Handle user exit from the room
    if request.method == 'POST' and 'exitButton' in request.POST:
         # Call disconnect_user to mark the user as inactive in the room
        Connected.disconnect_user(user, room_name)
        return redirect('index')
        


    # Handle sending messages
    if request.method == 'POST':
        message = request.POST.get('message')
        if message:
            new_message = Message.objects.create(room=room, sender=user.username, message=message)

    # Get all messages for the room
    messages = Message.objects.filter(room=room)
    
    # Get active users in the current room excluding the current user
    active_users = list(Connected.objects.filter(room_name=room_name, is_active=True).exclude(user=user).values_list('user__username', flat=True))
    
    # Add the current user to the active users list if not already present
    if user.username not in active_users:
        active_users.append(user.username)

    # Get online status for all active users
    online_status = {}
    for active_user in active_users:
        user_profile = UserProfileModel.objects.filter(user__username=active_user).first()
        if user_profile:
            online_status[active_user] = user_profile.online_status

    context = {
        "messages": messages,
        "user": user_profile.name,
        "room_name": room_name,
        "active_users": active_users,
        "online_status": online_status,
        "entry_message": f'{username} entered the chatroom.'
    }
    return render(request, 'message.html', context)

def user_profile_by_id(user_id):
    try:
        # Retrieve the user by ID or return a 404 error if not found
        user = get_object_or_404(User, id=user_id)
        
        # Access user properties
        username = user.username
        
        # Example: Get the room associated with the user (if any)
        try:
            room = Room.objects.get(user=user)
            room_name = room.room_name
        except Room.DoesNotExist:
            room_name = "No room associated with this user"
        
        return HttpResponse(f"Username: {username}, Room: {room_name}")
    except User.DoesNotExist:
        return HttpResponse("User not found", status=404)

def user_profile_by_username(username):
    # RETRIEVE THE USER BY USERNAME
    user = get_object_or_404(User, username=username)
    
    # NOW YOU HAVE THE USER OBJECT, YOU CAN ACCESS ITS PROPERTIES
    user_id = user.id
    # ADD ANY OTHER USER-RELATED OPERATIONS HERE
    
    return HttpResponse(f"User ID: {user_id}")

def disconnect(request, room_name, user):
    user_id=(Connected.get_online_users(room_name).first().user.id)
    Connected.disconnect_user(user_id, room_name)  
    print("HEY", user, room_name)
    return render(request, 'index.html')




def send_message(request, room_name, username):
    if request.method == 'POST':
        message = request.POST.get('message')
        if message:
            room = Room.objects.get(room_name=room_name)
            sender_username = request.user.username  # Assuming the sender is the currently logged-in user
            Message.objects.create(room=room, sender=sender_username, message=message)
    return redirect('room', room_name=room_name, username=username)
# import logging

# Get an instance of a logger
# logger = logging.getLogger(__name__)

@login_required
def enter_room(request, room_name):
    user = request.user
    user_id = user_id
    room = Room.objects.get(room_name=room_name)
    
    # Check if the user has previously entered the room
    if not Message.objects.filter(room=room, sender=user.id, message__contains="entered the chatroom").exists():
        # If not, create a message indicating the user has entered the chatroom
        entry_message = f'{user.username} entered the chatroom.'
        Message.objects.create(room=room, sender=user.id, message=entry_message)
    
    # Get all messages for the room
    messages = Message.objects.filter(room=room)
    
    return render(request, 'message.html', {'messages': messages})

def notify_active_users(room_name, new_user):
    active_users = Connected.objects.filter(room_name=room_name, is_active=True).exclude(user=new_user)
    for active_user in active_users:
        # Send a notification to each active user
        active_user.send_entry_message({'message': f'{new_user.username} has entered the chatroom.'})


def active_users(request):
    # Retrieve active users from ChatNotification model
    active_notifications = ChatNotification.objects.filter(is_seen=False)

    # Extract unique users from active notifications
    # active_users = active_notifications.values_list('user__username', flat=True).distinct()

    # return render(request, 'active_users.html', {'active_users': active_users})
    # Retrieve active users from Connected model
    active_users = Connected.objects.filter(is_active=True)
    return render(request, 'active_users.html', {'active_users': active_users})