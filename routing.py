from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/session/", consumers.SessionConsumer.as_asgi()),
    re_path(r"ws/playerList/", consumers.PlayerListConsumer.as_asgi()),
    re_path(r"ws/currentGames/", consumers.CurrentGameConsumer.as_asgi()),
]