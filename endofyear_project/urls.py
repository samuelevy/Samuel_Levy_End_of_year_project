"""
URL configuration for endofyear_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import django
from django.contrib import admin
from django.urls import include, path

from player import views
from signin import views as signin_views
from user_admin.views import AdminView
from .views import home_view
from player.views import LeaderBoardView
from user.views import UserView
from user.views import SearchView
from game.views import SearchPlayers

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('user.urls')),
    path('api/players/', include('player.urls')),
    path('', LeaderBoardView.as_view(), name='home'),
    path('admin_dashboard/', LeaderBoardView.as_view(), name='admin_dashboard'),
    path('player/', include('player.urls')),
    path('leaderboard/', LeaderBoardView.as_view(), name='leaderboard-html'),
    path('user/', include('user.urls')),
    path('signin/', include('django.contrib.auth.urls')),
    path('signin/', include('signin.urls')),
    path('searched/', SearchView.as_view(), name='searched'),
    path('user/', include('user.urls')),
    path('game/', include ('game.urls')),
    path('logoutUser/', signin_views.logoutUser, name='logout'),
    path('admin-api/', include('user_admin.urls')),
]
