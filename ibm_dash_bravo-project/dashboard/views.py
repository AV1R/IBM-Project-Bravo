from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate
# Create your views here.


def home(request):
    return render(request, 'dashboard/home.html')


def dashboard(request):
    return render(request, 'dashboard/dashboard.html')


def loginuser(request):
    if request.method == 'GET':
        return render(request, 'dashboard/loginuser.html', {'form': AuthenticationForm()})
    else:
        user = authenticate(
            request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'dashboard/loginuser.html', {'form': AuthenticationForm(), 'error': 'Username or password did not match'})
        else:
            login(request, user)
            return redirect('dashboard')


def signupuser(request):
    if request.method == 'GET':
        return render(request, 'dashboard/signupuser.html', {'form': UserCreationForm()})
    else:
        # Create a new user
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(
                    request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('dashboard')
            except IntegrityError:
                err = "The username has already been taken. Please choose a new username"
                return render(request, 'dashboard/signupuser.html', {'form': UserCreationForm(), 'error': err})

        else:
            # Tell the user the passwords didn't match
            err = "Passwords didn't match"
            return render(request, 'dashboard/signupuser.html', {'form': UserCreationForm(), 'error': err})


def logoutuser(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')
