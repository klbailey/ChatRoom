
#ChatProject>ChatApp>urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.CreateRoom, name='create-room'),
    # mapped to message view
    path('<str:room_name>/<str:username>/', views.MessageView, name='room'),
]