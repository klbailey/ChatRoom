#ChatProject>ChatApp>routing.py

from django.urls import path
from .consumers import ChatConsumer

# Create path points to consumer class Create URL that maps to this web socket of that room
websocket_urlpatterns = [
    path('ws/notification/<str:room_name>/', ChatConsumer.as_asgi()),
]