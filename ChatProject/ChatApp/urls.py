
#ChatProject>ChatApp>urls.py
from django.urls import path
from . import views


urlpatterns = [
    path('', views.CreateRoom, name='create-room'),
    # mapped to message view
    path('<str:room_name>/<str:username>/', views.MessageView, name='room'),
    path('user/<int:user_id>/', views.user_profile_by_id, name='user_profile_by_id'),
    path('user/by_username/<str:username>/', views.user_profile_by_username, name='user_profile_by_username'),
    # path('chat/<str:room_name>/<str:username>/', views.chat_view, name='chat'),
]
    