from django.urls import path

from . import views

app_name = "roundRobinWrapper"

urlpatterns = [
    path("", views.index, name="index"),
    path("api/players/", views.player_search_api, name="player_search_api"),
    path("api/player/", views.player_search_id_api, name="player_search_id_api"),
    path("api/active/", views.save_active_player_api, name="save_active_player_api"),
    path("api/getactive/", views.get_active_player_api, name="get_active_player_api"),
]
