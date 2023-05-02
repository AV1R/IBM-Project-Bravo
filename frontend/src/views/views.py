from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.


def home(request):
    return render(request, "public/home.html")


def loginuser(request):
    if request.method == 'GET':
        return render(request, 'public/login.html')
    else:
        user = {"username": request.POST['username'], "password": request.POST['password']}
        # user exists
        if user is None:
            # if not exists
            return render(request, 'public/login.html', {'form': user, 'error': 'Username or password did not match'})
        else:
            # login user if exists via endpoint and return json web token and create session
            return HttpResponse("Logged: username: " + user['username'] + " password: " + user['password'])
            # and redirect
            # return redirect('currenttodos')


def signupuser(request):
    if request.method == 'GET':
        return render(request, 'public/signup.html')
    else:
        # Create a new user
        user = {"username": request.POST['username'], "password": request.POST['password1']}
        if request.POST['password1'] == request.POST['password2']:
            try:
                # create user if not exists via endpoint and return json web token and create session
                return HttpResponse("Logged: " + user['username'] + " " + user['password'])
            except:
                err = "The username has already been taken. Please choose a new username"
                return render(request, 'public/signup.html', {'form': user, 'error': err})

        else:
            # Tell the user the passwords didn't match
            err = "Passwords didn't match"
            return render(request, 'public/signup.html', {'form': user, 'error': err})


def logoutuser(request):
    # Clean cookies and redirect
    return render(request, "public/home.html")
