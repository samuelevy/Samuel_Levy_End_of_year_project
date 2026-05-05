from django.urls import path

from player.views import ProfileView
from .views import UserView, SearchView

app_name = 'user'

urlpatterns = [
    path('', UserView.as_view(), name='user-list'),
    path('<int:user_id>/', UserView.as_view(), name='user-detail'),
    path('search/<str:name>/', UserView.as_view(), name='user_search_name'),
    path('profile/<int:user_id>/', UserView.as_view(), name='user_profile'),
    path('searched/', SearchView.as_view(), name='searched'),
    path('users/profile/<int:user_id>/', ProfileView.as_view(), name='user_profile'),
    path('<int:user_id>/change/', UserView.as_view(), name='user-change')
]