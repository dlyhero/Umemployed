from django.urls import path

from .consumers import ChatConsumer

# application = ProtocolTypeRouter({
#     'wwbsocket': AllowedHostsOriginValidator(
#         AuthMiddlewareStack(

#         )
#     )
# })

websocket_urlpatterns = [
    path("ws/notifications/<str:room_name>/", ChatConsumer.as_asgi()),
    # path('wss/notifications/<str:room_name>/', ChatConsumer.as_asgi()),
]
