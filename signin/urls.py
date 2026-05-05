from django.urls import path
from . import views

app_name = 'signin'

urlpatterns = [
    path('loginUser/', views.loginUser, name='login'),
    path('register/', views.register, name='register'),
    path('logoutUser/', views.logoutUser, name='logout'),
]