
#ChatProject>ChatApp>urls.py
from django.urls import path
from . import views
from .views import register_or_login

urlpatterns = [
    path('', views.CreateRoom, name='create-room'),
    # mapped to message view
    path('<str:room_name>/<str:username>/', views.MessageView, name='room'),
    path('user/<int:user_id>/', views.user_profile_by_id, name='user_profile_by_id'),
    path('user/by_username/<str:username>/', views.user_profile_by_username, name='user_profile_by_username'),
    # path('chat/<str:room_name>/<str:username>/', views.chat_view, name='chat'),
    # path('login/', register_or_login, name='login'),
    # path('register/', register_or_login, name='register'),
    path('register_or_login/', register_or_login, name='register_or_login'),
]
    