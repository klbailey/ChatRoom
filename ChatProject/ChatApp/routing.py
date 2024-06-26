
#ChatProject>ChatApp>routing.py
from django.urls import path
from .consumers import ChatConsumer, OnlineStatusConsumer
from . import consumers

# Create path points to consumer class Create URL that maps to this web socket of that room
websocket_urlpatterns = [
    path('ws/online/', OnlineStatusConsumer.as_asgi()),
# Dynamic WebSocket URL for handling notifications in different rooms
    path('ws/notification/<str:room_name>/', ChatConsumer.as_asgi()),
    # re_path(r'ws/chat/(?P<room_name>\w+)/$', ChatConsumer.as_asgi()),
    # handling online status WebSocket
    path('ws/online/', OnlineStatusConsumer.as_asgi()),
]

# New URL pattern for ChatConsumer with AuthMiddlewareStack
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

# Append the new URL pattern
websocket_urlpatterns += [
    path("chat/<room_name>/", AuthMiddlewareStack(URLRouter([
        path("chat/<room_name>/", ChatConsumer),
    ]))),
]