from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
import requests, json
from .decorators import session_auth_required, session_auth_not_required
import jwt
from django.conf import settings
import plotly.graph_objects as go

# Decorator token

# Create your views here.
localhost = "127.0.0.1"
port = 5000
url = f"http://{localhost}:{port}"


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


def chart_1():
    y_labels = [
        "AWS Certified Cloud Practitioner",
        "Certified Cloud Security Professional (CCSP)",
        "Certified Data Privacy Solutions Engineer (CDPSE)",
        "Certified Data Professional (CDP)",
        "Certified Ethical Hacker (CEH)",
        "Certified Information Security Manager (CISM)",
        "Certified Information Systems Security Professional (CISSP)",
        "Cisco Certified Internetwork Expert (CCIE)",
        "Cisco Certified Network Professional (CCNP)",
        "CompTIA (A+, Cloud+, Security+)",
        "Microsoft Certified Azure Solutions Architect Expert",
        "Information Technology Infrastructure Library (ITIL)",
        "Oracle MySQL Database Administration",
        "Project Management Professional (PMP)",
        "Salesforce Certified Development Lifecycle and Deployment Designer",
    ]
    y_values = [73, 58, 82, 90, 45, 60, 79, 65, 72, 85, 92, 78, 86, 93, 68]

    fig = go.Figure(
        data=[
            go.Bar(
                x=y_values,
                y=y_labels,
                orientation="h",
                marker=dict(color="#054ada"),  # IBM blue color
            )
        ],
        layout=go.Layout(
            xaxis=dict(title="Percentage"), yaxis=dict(title="Certification")
        ),
    )

    return fig.to_html(full_html=False, default_height=500, default_width=700)


def chart_2():
    labels = [
        "Finanace and operations",
        "Consulting",
        "Systems, Technology Lifecycles Services",
    ]
    values = [40, 30, 30]  # Example distribution percentages

    colors = ["#00008B", "#4169E1", "#00FFFF"]  # Dark blue, Royal blue, Cyan

    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                marker=dict(colors=colors),
                hole=0.4,  # Inner hole size (0-1)
            )
        ],
        layout=go.Layout(
            legend=dict(
                orientation="h", yanchor="bottom", y=-0.2
            ),  # Position the legend at the bottom
        ),
    )

    return fig.to_html(full_html=False, default_height=500, default_width=700)


def chart_3():
    x_top = list(range(1, 6))  # IDs for top 5
    y_top = [12, 10, 8, 6, 5]  # Values for top 5

    x_bottom = list(range(6, 11))  # IDs for bottom 5
    y_bottom = [3, 2, 2, 1, 0]  # Values for bottom 5

    colors_top = ["#008000"] * 5  # Green bars
    colors_bottom = ["#FF0000"] * 5  # Red bars

    fig = go.Figure()
    fig.add_trace(go.Bar(x=x_top, y=y_top, marker=dict(color=colors_top), name="Top 5"))
    fig.add_trace(
        go.Bar(
            x=x_bottom, y=y_bottom, marker=dict(color=colors_bottom), name="Bottom 5"
        )
    )

    fig.update_layout(
        xaxis=dict(title="ID"),
        yaxis=dict(title="Value"),
        barmode="group",  # Display bars side by side
    )

    return fig.to_html(full_html=False, default_height=500, default_width=700)


def chart_4():
    certifications = [
        "AWS Certified Cloud Practitioner",
        "Certified Cloud Security Professional (CCSP)",
        "Certified Data Privacy Solutions Engineer (CDPSE)",
        "Certified Data Professional (CDP)",
        "Certified Ethical Hacker (CEH)",
        "Certified Information Security Manager (CISM)",
        "Certified Information Systems Security Professional (CISSP)",
        "Cisco Certified Internetwork Expert (CCIE)",
        "Cisco Certified Network Professional (CCNP)",
        "CompTIA (A+, Cloud+, Security+)",
        "Microsoft Certified Azure Solutions Architect Expert",
        "Information Technology Infrastructure Library (ITIL)",
        "Oracle MySQL Database Administration",
        "Project Management Professional (PMP)",
    ]

    percentages = {
        "AWS Certified Cloud Practitioner": 80,
        "Certified Cloud Security Professional (CCSP)": 65,
        "Certified Data Privacy Solutions Engineer (CDPSE)": 45,
        "Certified Data Professional (CDP)": 70,
        "Certified Ethical Hacker (CEH)": 50,
        "Certified Information Security Manager (CISM)": 75,
        "Certified Information Systems Security Professional (CISSP)": 85,
        "Cisco Certified Internetwork Expert (CCIE)": 30,
        "Cisco Certified Network Professional (CCNP)": 55,
        "CompTIA (A+, Cloud+, Security+)": 60,
        "Microsoft Certified Azure Solutions Architect Expert": 90,
        "Information Technology Infrastructure Library (ITIL)": 40,
        "Oracle MySQL Database Administration": 75,
        "Project Management Professional (PMP)": 70,
    }

    colors = [
        "#054ada",  # IBM blue color
        "#00BFFF",  # Deep sky blue
        "#00FFFF",  # Cyan
        "#008080",  # Teal
        "#008000",  # Green
        "#FF4500",  # Orange red
        "#FF0000",  # Red
        "#8B008B",  # Dark magenta
        "#9400D3",  # Dark violet
        "#800080",  # Purple
        "#FFD700",  # Gold
        "#A9A9A9",  # Dark gray
        "#B22222",  # Fire brick
        "#FFA500",  # Orange
    ]

    values = ["Certificado", "No certificado"]

    fig = go.Figure(
        data=[
            go.Pie(
                labels=values,
                values=list(percentages.values()),
                marker=dict(colors=colors),
                hole=0.4,  # Inner hole size (0-1)
            )
        ],
        layout=go.Layout(
            legend=dict(
                orientation="h", yanchor="bottom", y=-0.2
            ),  # Position the legend at the bottom
            updatemenus=[
                dict(
                    buttons=[
                        dict(
                            label=cert,
                            method="update",
                            args=[
                                {
                                    "values": [
                                        [percentages[cert], 100 - percentages[cert]]
                                    ]
                                }
                            ],
                        )
                        for cert in certifications
                    ],
                    direction="down",
                    showactive=True,
                    x=0.5,
                    xanchor="center",
                    y=1.1,
                    yanchor="top",
                )
            ],
        ),
    )

    return fig.to_html(full_html=False, default_height=500, default_width=700)


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


@session_auth_required
def user_settings(request):
    return render(request, "private/user-settings.html")


@session_auth_required
def add(request):
    return render(request, "private/add.html")


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
        dashboards = [
            {"id": 1, "title": "DSH 1", "data": _data["dashboard"][:10]},
            {"id": 2, "title": "DSH 2", "data": _data["dashboard"][:5]},
            {"id": 3, "title": "DSH 3", "data": _data["dashboard"][:2]},
        ]
        chart_1div = chart_1()
        chart_2div = chart_2()
        chart_3div = chart_3()
        chart_4div = chart_4()
        return render(
            request,
            "private/dashboard.html",
            {
                "dashboards": dashboards,
                "user": userContext["first_name"],
                "chart_1div": chart_1div,
                "chart_2div": chart_2div,
                "chart_3div": chart_3div,
                "chart_4div": chart_4div,
            },
        )


def logout(request):
    # Clean cookies and redirect
    request.session.flush()
    return redirect("login")
