
#ChatProject>ChatApp>views.py
from django.shortcuts import render, redirect
from .models import *
from django.contrib.auth import authenticate, login
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from django.http import Http404, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from .models import Connected, UserProfileModel
from django.contrib.auth.decorators import login_required
from .models import UserProfileModel, Room
from django.urls import reverse
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
    # Get or create the User object
    user, _ = User.objects.get_or_create(username=username)

    # Set user as active in the room
    # connected_instance, _ = Connected.objects.get_or_create(user=user, room_name=room_name, defaults={'channel_name': 'default'})
    # connected_instance.is_active = True
    # connected_instance.last_activity = timezone.now()  # Update last activity time
    # connected_instance.save()
    # Set user as active in the room
    Connected.set_user_active(user, room_name, is_active=True)

    # Update user's online status
    # user_profile, _ = UserProfileModel.objects.get_or_create(user=user)
    # user_profile.online_status = True
    # user_profile.save()
        # Update user's online status
    Connected.set_user_active(user, room_name, is_active=True)

    
    # Get room object by name
    room = Room.objects.get(room_name=room_name)

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

    # Debug output to check user and active_users
    print("User:", user.username)
    print("Active Users:", active_users)

    if request.method == 'POST':
        message = request.POST['message']
        new_message = Message(room=room, sender=user.username, message=message)
        new_message.save()

    messages = Message.objects.filter(room=room)
    
    context = {
        "messages": messages,
        "user": user.username,
        "room_name": room_name,
        "active_users": active_users,
        "online_status": online_status
    }
    return render(request, 'message.html', context)

# Register / Login
# def register_or_login(request):
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         password = request.POST.get('password')
#         room_name = request.POST.get('room')

#         if not username or not password or not room_name:
#             return HttpResponseBadRequest("Missing username, password, or room name")

#         user = authenticate(request, username=username, password=password)
#         if user is not None:
#             print("User authenticated:", user.username)
#         else:
#             print("Creating new user...")
#             try:
#                 # User doesn't exist, create a new user
#                 new_user = User.objects.create_user(username=username, password=password)
#                 print("New user created:", new_user.username)
#                 user = authenticate(request, username=username, password=password)
#                 if user is not None:
#                     print("User authenticated after creation:", user.username)
#                     login(request, user)
#                 else:
#                     print("Failed to authenticate newly created user")
#                     return HttpResponseBadRequest("Failed to authenticate newly created user")
#             except Exception as e:
#                 print("Error creating user:", e)
#                 return HttpResponseBadRequest("Error creating user")

#         # Set the username in the session
#         request.session['username'] = username

#         # Redirect the user to the messages page for the selected room
#         return redirect('room', room_name=room_name, username=username)
#     else:
#         # If it's a GET request, just display the registration/login page
#         rooms = Room.objects.all().values_list('room_name', flat=True)
#         return render(request, 'index.html', {'rooms': rooms})


#  # INCORPORATE LINES 129-156 in MessageView
# def register_or_login(request):
#     print("You need to wokr!")
#     if request.method == 'POST':
#         username = request.POST['username']
#         password = request.POST['password']
#         room_name = request.POST.get('room_name', None)

#         print(f"Received username: {username}, password: {password}, room_name: {room_name}")

#         user, created = User.objects.get_or_create(username=username)

#         if created:
#             user.set_password(password)
#             user.save()

#             print("New user created.")

#             profile, _ = UserProfileModel.objects.get_or_create(user=user, name=username)
#             profile.room_name = room_name
#             profile.save()

#             print("UserProfileModel instance created and saved.")

#             connected_instance, _ = Connected.objects.get_or_create(user=user, room_name=room_name)
#             connected_instance.save()

#             print("Connected instance created and saved.")

#         user = authenticate(request, username=username, password=password)
#         if user is not None:
#             login(request, user)
#             Connected.set_user_active(user, room_name)
#             print("User authenticated and set active.")
#             return redirect('message')
#         else:
#             error_message = "Failed to log in the user"
#             return render(request, 'index.html', {'error_message': error_message})

#     return render(request, 'message.html')

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