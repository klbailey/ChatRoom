#ChatProject>ChatApp>views.py
# Create your views here.
from django.shortcuts import render, redirect
from .models import *
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from django.http import Http404

def CreateRoom(request):
    if request.method == 'POST':
        username = request.POST['username']
        room = request.POST['room']
        # Either get room object or create if doesn't exist
        try:
            get_room = Room.objects.get(room_name=room)
            
            return redirect('room', room_name=room, username=username)
        # If room does not exist we will create it and save
        except Room.DoesNotExist:
            new_room = Room(room_name = room)
            new_room.save()
            # Set user as active in session
            request.session[f'room_{room}_{username}'] = True
            return redirect('room', room_name=room, username=username)
    rooms = Room.objects.all().values_list('room_name', flat=True)
    return render(request, 'index.html', {'rooms': rooms})

def MessageView(request, room_name, username):
    # Get room object by name
    get_room = Room.objects.get(room_name=room_name)

    # ****************************
       # Get active users in the current room
    active_users = [key.split('_')[-1] for key, value in request.session.items() if key.startswith(f'room_{room_name}_')]
    
    # Remove duplicates
    active_users = list(set(active_users))

    print("Active Users:", active_users)  # Add this line for debugging

    # Add the current user to the active users list if not already present
    if username not in active_users:
        active_users.append(username)
        # Update the session data
        request.session[f'room_{room_name}_{username}'] = True
    # *********************

    if request.method == 'POST':
        message = request.POST['message']

        print(message)

        new_message = Message(room=get_room, sender=username, message=message)
        new_message.save()

    get_messages= Message.objects.filter(room=get_room)
    
    context = {
        "messages": get_messages,
        "user": username,
        "room_name": room_name,
        # *******
        "active_users": active_users,  # Pass active users to the template
    }
    return render(request, 'message.html', context)
