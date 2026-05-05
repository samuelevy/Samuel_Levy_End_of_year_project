from urllib import request
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from .forms import CreateUserForm
from user.models import AppUser
from player.models import Player

# Create your views here.
def loginUser(request):
    if request.method=="POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirect to a success page.
            if user.role=="PLAYER":
                return redirect('home')
            elif user.role=="ADMIN":
                return redirect('admin-dashboard')
        else:
            # Return an 'invalid login' error message.
            messages.success(request, ("There Was An Error Logging In, Try Again..."))
            return redirect('login')
    else:
        return render(request, 'registration/login.html', {})
    
def register(request):
    if request.method=="POST":
        form=CreateUserForm(request.POST)
        if form.is_valid():
            name=form.cleaned_data['name']
            password=form.cleaned_data['password1']
            app_user=AppUser.objects.create(name=name, role="PLAYER")
            app_user.set_password(password)
            app_user.save()
            
            player=Player.objects.create(user=app_user, elo=1500, glicko=1500, glicko_rd=350)
            
            user=authenticate(username=name, password=password)
            login(request, user)
            messages.success(request, ("Registration Successful!"))
            return redirect('home')
    else:
        form=CreateUserForm()
    return render(request, 'registration/register.html', {'form':form})

def logoutUser(request):
    logout(request)
    messages.success(request, ("You were logged out, log back in!"))
    return redirect('login')
        