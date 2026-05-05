from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import AppUser
from django.db.models import Q
from django.db import transaction
import json

# Create your views here.
class UserView(View):
    
    #PARAMETERS AND CLASS FUNCTIONS
    def __init__(self, **kwargs): #setter
        super().__init__(**kwargs)
        self.user_id=None
        self.name=None
        self.role=None
        
    def get(self, request, user_id=None): # Handle GET requests
        #find by id:
        if user_id:
            user = get_object_or_404(AppUser, user_id=user_id)
            return JsonResponse({
                'user_id': user.user_id,
                'name': user.name,
                'role': user.role
            })
        #list all users:
        else:
            users= AppUser.objects.all()
            users_list = [
                {
                    'user_id': user.user_id,  # Extract each field
                    'name': user.name,
                    'role': user.role
                }
                for user in users  # Loop through all users
            ]
            return JsonResponse({'users': users_list})
            
    def post(self, request, user_id=None): # Handle POST requests to create a new user
        import json
        
        if user_id:
            return self.change_user(request, user_id)
        
        data = json.loads(request.body)
        user=AppUser(name=data.get('name'), role=data.get('role', 'PLAYER')) # Default role to 'PLAYER' if not provided
        user.set_password(data.get('password'))  # Hash the password before saving
        user.save()
        return JsonResponse({
            'message': 'User created successfully',
            'user_id': user.user_id  # Return the auto-generated ID
        }, status=201)
        
    def change_user(self, request, user_id):
        user=get_object_or_404(AppUser, user_id=user_id)
        data = json.loads(request.body)
        new_name = data.get('name', '').strip()
        if not new_name:
            return JsonResponse({
                'error': 'Username cannot be empty'
            }, status=400)
        if len(new_name) < 3:
            return JsonResponse({
                'error': 'Username must be at least 3 characters'
            }, status=400)
        with transaction.atomic():
            user.name = new_name
            user.save()
        
        return JsonResponse({
            'message': 'Username updated successfully',
            'new_name': new_name
        }, status=200)
        
##########################################################
    # GET methods for other classes
    @staticmethod
    def getbyid(user_id):
        return get_object_or_404(AppUser, user_id=user_id)
    @staticmethod
    def getbyname(name):
        return AppUser.objects.filter(name__icontains=name)
    def getall():
        return AppUser.objects.all()
    def getrole(self):
        return self.role
    
class SearchView(View):
    def post(self, request):
        query=request.POST.get('search', '')
        users = AppUser.objects.none()
        
        if query:
            users = AppUser.objects.filter(Q(name__icontains=query) | Q(user_id__icontains=query)).order_by('name')
            
            #Filter so players can only see players
            if hasattr(request.user, 'player_profile'):
                users = users.filter(role='PLAYER')
            
        return render(request, 'searched.html', {
            'query':query,
            'users': users
        })
        
    def get(self, request):
        return render(request, 'searched.html', {'query':'', 'users':[]})
        