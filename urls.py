from django.urls import path

from . import views

app_name = "roundRobinWrapper"

urlpatterns = [
    path("", views.index, name="index"),
    path("api/players/", views.player_search_api, name="player_search_api"),
    path("api/player/", views.player_search_id_api, name="player_search_id_api"),
    path("api/getactive/", views.get_active_player_api, name="get_active_player_api"),
    path("api/getnextgame/", views.generate_game_api, name="generate_game_api"),
    path("api/resetHistory/", views.reset_game_history_api, name="reset_game_history_api"),
    path("api/addactive/", views.add_active_player_api, name="add_active_player_api"),
    path("api/removeactive/", views.remove_active_player_api, name="remove_active_player_api"),
]
