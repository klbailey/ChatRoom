
#ChatProject>ChatApp>routing.py

from django.urls import path, re_path
from .consumers import ChatConsumer
from . import consumers

# Create path points to consumer class Create URL that maps to this web socket of that room
websocket_urlpatterns = [
    path('ws/notification/<str:room_name>/', ChatConsumer.as_asgi()),
    # re_path(r'ws/chat/(?P<room_name>\w+)/$', ChatConsumer.as_asgi()),
]

