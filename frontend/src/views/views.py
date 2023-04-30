from django.shortcuts import render
# Create your views here.


def home(request):
    return render(request, 'public/home.html')


def signupuser(request):
    return render(request, 'public/signup.html')


def loginuser(request):
    return render(request, 'public/login.html')


def logoutuser(request):
    return render(request, 'public/home.html')
