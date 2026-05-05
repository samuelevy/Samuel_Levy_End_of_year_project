from django.urls import path
from . import views

app_name="game"
urlpatterns = [
    path('api/search-players/', views.SearchPlayers.as_view(), name='search_players_api'),
    path('api/record-game/', views.RecordGame.as_view(), name='record_game_api'),
    path('', views.RecordGame.as_view(), name='record_game_page'),
]
