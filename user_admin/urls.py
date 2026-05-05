from django.urls import path
from .views import AdminView

app_name = 'user_admin'

urlpatterns = [
    # RESTful user operations
    path('users/', AdminView.as_view(), name='user-list-create'),
    path('users/<int:user_id>/', AdminView.as_view(), name='user-detail'),
    
    # Special admin promotion
    path('users/<int:user_id>/make-admin/', AdminView.as_view(), name='user-make-admin'),
    
    #Delete user
    path('users/<int:user_id>/delete/', AdminView.as_view(), name='user-delete'),
]
