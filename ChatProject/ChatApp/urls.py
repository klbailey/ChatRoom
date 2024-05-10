
#ChatProject>ChatApp>urls.py
from django.urls import path, re_path
from django.contrib.auth.decorators import login_required
from . import views
from .consumers import ChatConsumer

urlpatterns = [
    path('', views.CreateRoom, name='create-room'),
    # mapped to message view
    path('<str:room_name>/<str:username>/', login_required(views.MessageView), name='room'),
    path('disconnect/<str:room_name>/<str:user>/', views.disconnect),
    # path('index/', views.index, name='index'),
    re_path(r'ws/chat/(?P<room_name>\w+)/$', ChatConsumer.as_asgi()),
    path('active_users/<str:room_name>/', views.active_users, name='active_users'), 
    path('<str:room_name>/<str:username>/send_message/', login_required(views.send_message), name='send_message'),
]

    