import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from django.urls import path

import notifications.routing
from messaging import consumers

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "umemployed.settings")

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AuthMiddlewareStack(
            URLRouter(
                [
                    *notifications.routing.websocket_urlpatterns,
                    path("ws/chat/<int:conversation_id>/", consumers.ChatConsumer.as_asgi()),
                ]
            )
        ),
    }
)
