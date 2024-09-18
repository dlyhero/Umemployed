# your_project_name/asgi.py

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path
from messaging import consumers
import notifications.routing


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umemployed.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter([
            notifications.routing.websocket_urlpatterns,
            path('ws/chat/<int:conversation_id>/', consumers.ChatConsumer.as_asgi()),

        ])
    ),
})
