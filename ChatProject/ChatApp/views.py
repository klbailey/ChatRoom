#ChatProject>ChatApp>views.py
from django.shortcuts import render, redirect
from .models import *
from django.contrib.auth import authenticate, login
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from .models import Connected

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



def MessageView(request, room_name, username):
    # Get or create a Connected instance for the user in the room
    connected_instance, created = Connected.objects.get_or_create(user=request.user, room_name=room_name, defaults={'channel_name': 'default'})
    
    # Set user as active in the room
    connected_instance.is_active = True
    connected_instance.save()

    # Update user's online status
    UserProfileModel.objects.filter(user=request.user).update(online_status=True)
    
    # Get room object by name
    get_room = Room.objects.get(room_name=room_name)

    # Get active users in the current room
    active_users = Connected.objects.filter(room_name=room_name, is_active=True).values_list('user__username', flat=True)
    
    # Convert queryset to list
    active_users = list(active_users)

    print("Active Users:", active_users)  # Add this line for debugging

    # Add the current user to the active users list if not already present
    if username not in active_users:
        active_users.append(username)
        # Update the session data
        request.session[f'room_{room_name}_{username}'] = True

    if request.method == 'POST':
        message = request.POST['message']

        print(message)

        new_message = Message(room=get_room, sender=username, message=message)
        new_message.save()

    get_messages = Message.objects.filter(room=get_room)
    
    context = {
        "messages": get_messages,
        "user": username,
        "room_name": room_name,
        "active_users": active_users,  # Pass active users to the template
    }
    return render(request, 'message.html', context)

# Register / Login
def register_or_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        room_name = request.POST.get('room_name', None)  # Get the room_name from the form

        user = User.objects.filter(username=username).first()
        if user is not None:
            # Log the user in
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('message')
            else:
                error_message = "Invalid username or password"
                return render(request, 'index.html', {'error_message': error_message})
        else:
            # Create a new user
            new_user = User.objects.create_user(username=username, password=password)
            # Create UserProfileModel instance for the new user
            UserProfileModel.objects.create(user=new_user, name=username, room_name=room_name)
            # Log the user in
            user = authenticate(request, username=username, password=password)
            login(request, user)
            return redirect('index')

    return render(request, 'message.html')



def user_profile_by_id(request, user_id):
    # RETRIEVE THE USER BY ID
    user = get_object_or_404(User, id=user_id)
    
    # NOW YOU HAVE THE USER OBJECT, YOU CAN ACCESS ITS PROPERTIES
    username = user.username
    # ADD ANY OTHER USER-RELATED OPERATIONS HERE
    
    return HttpResponse(f"Username: {username}")

def user_profile_by_username(request, username):
    # RETRIEVE THE USER BY USERNAME
    user = get_object_or_404(User, username=username)
    
    # NOW YOU HAVE THE USER OBJECT, YOU CAN ACCESS ITS PROPERTIES
    user_id = user.id
    # ADD ANY OTHER USER-RELATED OPERATIONS HERE
    
    return HttpResponse(f"User ID: {user_id}")