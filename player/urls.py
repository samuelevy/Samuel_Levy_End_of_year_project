from django.urls import path
from .views import PlayerView, LeaderBoardView, ProfileView

urlpatterns = [
    path('api/leaderboard/', PlayerView.as_view(), name='player-leaderboard'),

    path('', PlayerView.as_view(), name='player-list-create'),
    path('<int:user_id>/', PlayerView.as_view(), name='player-detail'),
    path('<int:user_id>/update-rating/', PlayerView.as_view(), name='player-update-rating'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/<int:user_id>/', ProfileView.as_view(), name='profile'), 
]