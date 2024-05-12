#Store>bike>urls.py
from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='home'), 
    path('track-order/', views.track_order, name='track_order'),
    path('products/', views.product_list, name='product_list'),
    path('products/<int:pk>/', views.product_detail, name='product_detail'),
    path('orders/', views.order_list, name='order_list'),
    path('orders/<int:pk>/', views.order_detail, name='order_detail'),
    path('road-bikes/', views.road_bikes, name='road_bikes'),
    path('mountain-bikes/', views.mountain_bikes, name='mountain_bikes'),
    path('e-bikes/', views.e_bikes, name='e_bikes'),
    path('chatbox/', views.chatbox, name='chatbox'), 
    path('favicon.ico', views.favicon, name='favicon'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
]
