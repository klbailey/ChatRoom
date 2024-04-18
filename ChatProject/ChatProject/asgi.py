"""
ASGI config for ChatProject project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""
#ChatProject>ChatProject>asgi.py
import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from ChatApp import routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ChatProject.settings')

django_asgi_app = get_asgi_application()

# Map web socket URL (coming from routing.py)
application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": URLRouter(
        routing.websocket_urlpatterns
    )
}) 
