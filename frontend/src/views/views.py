from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
import requests, json
from .decorators import session_auth_required, session_auth_not_required
import jwt
from django.conf import settings

# Decorator token

# Create your views here.
localhost = "127.0.0.1"
port = 5000
url = f"http://{localhost}:{port}/"


@session_auth_required
def getUserContext(request):
    if "jwt_token" in request.session:
        jwt_token = request.session["jwt_token"]
        try:
            user = jwt.decode(jwt_token, settings.SECRET_KEY, algorithms=["HS256"])
            request.session["user"] = user
            return user
            # Do something with the email
        except jwt.DecodeError:
            # Handle invalid token
            pass
    else:
        # Handle case when jwt_token is not present in session
        pass


@session_auth_not_required
def login(request):
    if request.method == "POST":
        # Enviar las credenciales al backend Flask para autenticar
        user = {
            "email": request.POST["email"],
            "password": request.POST["password"],
        }

        headers = {"Content-Type": "application/json"}  # Specify JSON content type

        response = requests.post(f"{url}/login", data=json.dumps(user), headers=headers)
        if response.status_code == 200:
            # Si el inicio de sesión fue exitoso, guardar el token JWT en la sesión de Django
            token = response.json()
            request.session["jwt_token"] = token["token"]
            # Redirigir a la vista protegida
            return redirect("dashboard")
        else:
            # Si el inicio de sesión falló, mostrar el mensaje de error
            return render(
                request,
                "public/login.html",
                {"form": user, "error": "Email o contraseña invalidos"},
            )

    return render(request, "public/login.html")


@session_auth_not_required
def home(request):
    return render(request, "public/home.html")


@session_auth_not_required
def signup(request):
    if request.method == "POST":
        # Enviar las credenciales al backend Flask para autenticar
        user = {
            "email": request.POST["email"],
            "first_name": request.POST["first_name"],
            "second_name": request.POST["second_name"],
            "password": request.POST["password"],
            "password1": request.POST["password1"],
        }
        if user["password"] == user["password1"]:
            headers = {"Content-Type": "application/json"}  # Specify JSON content type

            response = requests.post(
                f"{url}/register", data=json.dumps(user), headers=headers
            )
            if response.status_code == 200:
                # Si el inicio de sesión fue exitoso, guardar el token JWT en la sesión de Django
                token = response.json()
                request.session["jwt_token"] = token["token"]
                # Redirigir a la vista protegida
                return redirect("dashboard")
            else:
                # Si el inicio de sesión falló, mostrar el mensaje de error
                return render(
                    request,
                    "public/signup.html",
                    {"form": user, "error": "El email ya esta registrado"},
                )
        else:
            # Tell the user the passwords didn't match
            err = "La contraseña no coincide"
            return render(request, "public/signup.html", {"form": user, "error": err})
    return render(request, "public/signup.html")


@session_auth_required
def dashboard(request):
    userContext = getUserContext(request)
    userEmail = {"email": userContext["email"]}
    headers = {"Content-Type": "application/json"}  # Specify JSON content type

    response = requests.get(f"{url}/dash", data=json.dumps(userEmail), headers=headers)
    _data = response.json()
    if "error" in _data:
        return render(
            request,
            "private/dashboard.html",
            {"error": f"No existe ningun dashboard", "user": userContext["first_name"]},
        )
    else:
        data = _data["dashboard"]
        return render(
            request,
            "private/dashboard.html",
            {"data": data[:10], "user": userContext["first_name"]},
        )


def logout(request):
    # Clean cookies and redirect
    request.session.flush()
    return redirect("login")
