from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import requests
# Create your views here.
localhost='127.0.0.1'
port=5000
url=f'http://{localhost}:{port}/'

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

def getDashByUser(user):
    # get dashboard by user
    # get data from endpoint
    certificates=f'{url}dash-api'
    response = requests.get(certificates)
    
    if response.status_code == 200:
        try:
            data = response.json()
            return data['data']
        except:
            return []
    else:
        return []

def dashboard(request):
    data= getDashByUser("uid")
    # for item in data:
    #     print(item["_id"],"\n\n\n")
    # print("JSON RESPONSE:\n",data['dashboard'][0],"\n json works")
    if data==[]:
        return render(request, 'private/dashboard.html', {"error":f"No existe ningun dashboard"})
    else:    
        return render(request, 'private/dashboard.html', {"data":data[:10]})
    

def logoutuser(request):
    # Clean cookies and redirect
    return render(request, "public/home.html")
