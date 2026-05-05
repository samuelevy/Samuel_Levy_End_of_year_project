from django.contrib import messages
from urllib import request
from django.shortcuts import get_object_or_404, redirect, render
from player.models import Player
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from user.models import AppUser
from user_admin.models import Admin
from .permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import connection


# Create your views here.
class AdminView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    #CALL METHODS
    def post(self, request, user_id=None):
        if user_id and 'make-admin' in request.path:
            return self.makeAdmin(request, user_id)
        if user_id and 'delete' in request.path:
            return self.deleteUser(request, user_id)
        return self.createUser(request)
    def put(self, request, user_id):
        return self.updateUser(request, user_id)
    def get(self, request):
        return self.listUsers(request)
    def delete(self, request, user_id=None):
        if not user_id:
            return Response(
                {'error': 'User ID required for deletion'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        return self.deleteUser(request, user_id)
    
    #CREATE USER    
    def createUser(self, request):
        # Logic to create a new user
        name = request.data.get('name')
        role = request.data.get('role', 'player')
        if not name:
            return Response({'error': 'Name is required'}, status=400)
        if role not in ['player', 'admin']:
            return Response({'error': 'Invalid role'}, status=400)
        
        # Create user logic here
        try:
            user = AppUser.objects.create(name=name, role=role)
            if role == 'player':
                Player.objects.create(user=user,
                                      elo=1500.00,
                                      glicko=1500.00,
                                      glicko_rd=350.0,
                                      volatility=0.06)
            elif role == 'admin':
                Admin.objects.create(
                    user=user
                )
            return Response({'message': 'User created successfully', 'user_id': user.id}, status=201)
        except Exception as e:
            return Response({'error': str(e)}, status=500)
        
    #DELETE USER
    def deleteUser(self, request, user_id):
        # Logic to delete a user
        user = get_object_or_404(AppUser, user_id=user_id)
        if hasattr(request.user, 'user_id') and request.user.user_id == user_id:
            return Response(
                {'error': 'Cannot delete your own account'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        try:
            # Store user info before deletion
            user_info = {
                'user_id': user.user_id,
                'name': user.name,
                'role': user.role
            }
            
            # Delete user (CASCADE will delete related Player/Admin records)
            with connection.cursor() as cursor:
            # Delete related records first
                cursor.execute("DELETE FROM player WHERE user_id = %s", [user_id])
                cursor.execute("DELETE FROM admin_user WHERE user_id = %s", [user_id])
                cursor.execute("DELETE FROM app_user WHERE user_id = %s", [user_id])
            
            return redirect('home')
            
        except Exception as e:
            return Response(
                {'error': f'Failed to delete user: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    #UPDATE USER
    def updateUser(self, request, user_id):
        user = get_object_or_404(AppUser, user_id=user_id)
        name= request.data.get('name')
        role= request.data.get('role')
        if name:
            user.name = name
        if role in ['player', 'admin']:
            user.role = role
        user.save()
        return Response({'message': 'User updated successfully'}, status=200)
    
    #LIST USERS
    def listUsers(self, request):
        users = AppUser.objects.all()
        users_data = [{'user_id': u.user_id, 'name': u.name, 'role': u.role} for u in users]
        return Response(users_data, status=200)
    
    #MAKE ADMIN
    @transaction.atomic
    def makeAdmin(self, request, user_id):
        user = get_object_or_404(AppUser, user_id=user_id)
        
        try:
            player = Player.objects.get(user=user)
            player.delete()
        except Player.DoesNotExist:
            pass
        
        user.role = 'ADMIN'
        user.save()
        
        admin, created = Admin.objects.get_or_create(user=user)
        
        if created:
            messages.success(request, f'{user.name} has been promoted to admin successfully!')
        else:
            messages.info(request, f'{user.name} was already in the admin table')
        
        return redirect('home')
        
    def enterResults(self, request):
        # Logic to enter game results
        pass