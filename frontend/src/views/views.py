import json

import jwt
import plotly.graph_objects as go
import requests
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render

from .decorators import session_auth_not_required, session_auth_required

# Decorator token

# Create your views here.
localhost = "127.0.0.1"
port = 5000
url = f"http://{localhost}:{port}"


@session_auth_required
def search(request):
    if request.method == "POST":
        print("on search python")
        payload = json.loads(request.body)
        dshId = payload.get("dsh")
        target = payload.get("target")
        userContext = getUserContext(request)
        print(dshId, target, userContext["email"])
        search = {"owner": userContext["email"], "dsh": dshId, "target": target}
        headers = {"Content-Type": "application/json"}  # Specify JSON content type
        response = requests.post(
            f"{url}/dash/search", data=json.dumps(search), headers=headers
        )
        print(response.status_code)
        if response.status_code == 200:
            print("on python response")
            _data = response.json()
            # print(_data)
            if _data:
                table = _data["table"]
                return JsonResponse(
                    {"table": table}
                )  # Return the table content as JSON
        else:
            print("entro except")
            pass

    # If no data is found or if the request method is not POST, return an empty JSON response
    return JsonResponse({})


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


def chart_1(owner, dsh):
    try:
        match = {"owner": owner, "dsh": dsh}
        headers = {"Content-Type": "application/json"}  # Specify JSON content type
        response = requests.get(
            f"{url}/dash/chart1", data=json.dumps(match), headers=headers
        )

        data = response.json()

        y_labels = [entry["_id"] for entry in data]
        y_values = [entry["count"] for entry in data]

        # Gradient of IBM blue colors
        colors = [
            "#004144",
            "#005d5d",
            "#004144",
            "#005d5d",
            "#004144",
            "#00539a",
            "#003a6d",
            "#00539a",
            "#003a6d",
            "#00539a",
            "#002d9c",
            "#0043ce",
            "#002d9c",
            "#0043ce",
            "#002d9c",
        ]

        fig = go.Figure(
            data=[
                go.Bar(
                    x=y_values,
                    y=y_labels,
                    orientation="h",
                    marker=dict(color=colors, line=dict(color=colors)),
                    text=y_values,
                    textposition="auto",
                    textfont=dict(color="white"),
                )
            ],
            layout=go.Layout(
                title="Certification Bar Chart",
                title_font=dict(color="#f4f4f4"),
                # xaxis=dict(title="Percentage", title_font=dict(color="#c6c6c6")),
                yaxis=dict(
                    # title="Certification",
                    # title_font=dict(color="#c6c6c6"),
                    tickfont=dict(color="#c6c6c6", size=12),  # Set a smaller font size
                    automargin=True,
                ),
                plot_bgcolor="#21272a",
                paper_bgcolor="#21272a",
                margin=dict(l=200, r=25, t=60, b=50, pad=10),
            ),
        )
        fig.update_layout(
            annotations=[
                dict(
                    xref="paper",
                    yref="paper",
                    x=-0.25,
                    y=1.135,
                    text="[i]",
                    showarrow=False,
                    hovertext="This chart displays the quantity of completed certifications for each of the ICO's Top 15 certifications.",
                    hoverlabel=dict(bgcolor="#21272a", font=dict(color="white")),
                )
            ]
        )

        return fig.to_html(full_html=False, config={"responsive": True})
    except requests.exceptions.RequestException as e:
        return str(e)


def chart_2(owner, dsh):
    """labels = [
        "Finanace and operations",
        "Consulting",
        "Systems, Technology Lifecycles Services",
    ]
    values = [40, 30, 30]  # Example distribution percentages"""

    try:
        match = {"owner": owner, "dsh": dsh}
        headers = {"Content-Type": "application/json"}  # Specify JSON content type
        response = requests.get(
            f"{url}/dash/chart2", data=json.dumps(match), headers=headers
        )

        data = response.json()
        # print(data)
        """labels=[]
        values=[]
        for entry in data:
            labels.append(entry["org"])
            values.append(entry["percentage"])
            print()"""

        labels = [entry["org"] for entry in data]
        values = [entry["percentage"] for entry in data]

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
                title="Department Distribution",
                title_font=dict(color="#f4f4f4"),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.2,
                    font=dict(color="white"),  # Set annotation text color to white
                ),  # Position the legend at the bottom
                plot_bgcolor="#21272a",  # Transparent plot background
                paper_bgcolor="#21272a",  # Transparent paper background
                margin=dict(
                    b=12,  # Add spacing on the bottom side
                ),
            ),
        )
        fig.update_layout(
            annotations=[
                dict(
                    xref="paper",
                    yref="paper",
                    x=0.73,
                    y=1.24,
                    text="[i]",
                    showarrow=False,
                    hovertext="Employee distribution across all organizations.",
                    hoverlabel=dict(bgcolor="#21272a", font=dict(color="white")),
                )
            ]
        )

        return fig.to_html(full_html=False, config={"responsive": True})
    except requests.exceptions.RequestException as e:
        # Exception handling code...
        return str(e)


def chart_3(owner, dsh):
    """top_ids = list(range(1, 6))
    bottom_ids = list(range(6, 11))

    top_values = [12, 10, 8, 6, 5]  # Example values for the top 5
    bottom_values = [3, 2, 2, 1, 0]  # Example values for the bottom 5"""

    try:
        match = {"owner": owner, "dsh": dsh}
        headers = {"Content-Type": "application/json"}  # Specify JSON content type
        response = requests.get(
            f"{url}/dash/chart3", data=json.dumps(match), headers=headers
        )

        data = response.json()

        top_ids = [entry["_id"] for entry in data[0]["top5"]]
        bottom_ids = [entry["_id"] for entry in data[0]["bottom5"]]

        top_values = [entry["count"] for entry in data[0]["top5"]]
        bottom_values = [entry["count"] for entry in data[0]["bottom5"]]

        colors = ["#24a148"] * 5 + ["#fa4d56"] * 5  # Green for top 5, Red for bottom 5

        fig = go.Figure(
            data=[
                go.Bar(
                    x=top_ids + bottom_ids,
                    y=top_values + bottom_values,
                    marker=dict(
                        color=colors, line=dict(color=colors, width=1)
                    ),  # Set bar colors and white line border
                    text=top_values + bottom_values,
                    textposition="auto",
                    textfont=dict(color="white"),  # Set text color to white
                )
            ]
        )

        fig.update_layout(
            # title={
            #    'text': 'Top 5 and Bottom 5 Values',
            #    'font': {'color': 'white'}  # Set title text color to white
            # },
            title="Top 5 | Bottom 5",
            title_font=dict(color="#f4f4f4"),
            xaxis={
                "title": "IDs",
                "title_font": {
                    "color": "white"
                },  # Set x-axis title text color to white
                "tickfont": {
                    "color": "white"
                },  # Set x-axis tick labels text color to white
            },
            yaxis={
                "title": "",
                "title_font": {
                    "color": "white"
                },  # Set y-axis title text color to white
                "tickfont": {
                    "color": "white"
                },  # Set y-axis tick labels text color to white
            },
            plot_bgcolor="#21272a",  # Transparent plot background
            paper_bgcolor="#21272a",  # Transparent paper background
            annotations=[
                dict(
                    xref="paper",
                    yref="paper",
                    x=0.45,
                    y=1.31,
                    text="[i]",
                    showarrow=False,
                    hovertext="Top 5 and Bottom 5 places per quantity of certifications.",
                    hoverlabel=dict(bgcolor="#21272a", font=dict(color="white")),
                )
            ],
        )

        return fig.to_html(full_html=False, config={"responsive": True})
    except requests.exceptions.RequestException as e:
        # Exception handling code...
        return str(e)


def chart_4(owner, dsh):
    """userContext = getUserContext(request)
    userEmail = {"email": userContext["email"]}
    headers = {"Content-Type": "application/json"}"""

    """userContext = getUserContext(request)
    userEmail = {"email": userContext["email"]}
    headers = {"Content-Type": "application/json"}  # Specify JSON content type
    response = requests.get(f"{url}/dash/chart1", data=json.dumps(userEmail), headers=headers)"""

    try:
        """response = requests.get(
            f"{url}/dash/chart1", data=json.dumps(user), headers=headers
        )"""
        match = {"owner": owner, "dsh": dsh}
        headers = {"Content-Type": "application/json"}  # Specify JSON content type
        response = requests.get(
            f"{url}/dash/chart4", data=json.dumps(match), headers=headers
        )

        data = response.json()

        certifications = [entry["certification"] for entry in data]
        percentages = {entry["certification"]: entry["percentage"] for entry in data}

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

        values = ["Certified", "Not certified"]

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
                title="Certification Distribution",
                title_font=dict(color="#f4f4f4"),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.2,
                    font=dict(color="white"),  # Set annotation text color to white
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
                        showactive=False,
                        x=0.5,
                        xanchor="center",
                        y=1.1,
                        yanchor="top",
                        bgcolor="#1c1c1c",  # Set dropdown background color to black
                        font=dict(
                            color="gray", size=10
                        ),  # Set dropdown text color to white
                        # activecolor="gray",  # Set active dropdown color to gray
                    )
                ],
                plot_bgcolor="#21272a",  # Transparent plot background
                paper_bgcolor="#21272a",  # Transparent paper background
                margin=dict(
                    t=80,  # Add spacing on the top side
                    b=12,  # Add spacing on the bottom side
                ),
            ),
        )

        return fig.to_html(full_html=False, config={"responsive": True})
    except requests.exceptions.RequestException as e:
        # Exception handling code...
        return str(e)


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
    userContext = getUserContext(request)
    if request.method == "POST":
        # Check if a file is present in the request
        if "file" not in request.FILES:
            return render(request, "private/add.html", {"error": "No file selected"})

        file = request.FILES["file"]
        email = userContext["email"]

        try:
            # Create a dictionary payload
            payload = {"email": email}

            # Make a POST request to the backend endpoint
            files = {"file": file}
            response = requests.post(f"{url}/upload", data=payload, files=files)
            # print(response)

            if response.status_code == 200:
                return render(
                    request,
                    "private/add.html",
                    {"success": "Your data has been imported successfully"},
                )
            else:
                return render(
                    request,
                    "private/add.html",
                    {
                        "error": "An error occurred while processing the file, make sure you adhere to the standard format and use a .csv file"
                    },
                )

        except Exception as e:
            return render(
                request,
                "private/add.html",
                {
                    "error": "An error occurred while uploading the file, make sure you have a stable connection"
                },
            )

    return render(request, "private/add.html")


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
            {
                "error": f"No existe ningun dashboard",
                "user": userContext["first_name"],
            },
        )
    else:
        data1 = []
        data2 = []
        data3 = []
        for item in _data["dashboard"]:
            if item["dsh"] == 1:
                data1.append(item)
            elif item["dsh"] == 2:
                data2.append(item)
            elif item["dsh"] == 3:
                data3.append(item)

        dashboards = []
        if data1:
            dashboards.append(
                {
                    "id": 1,
                    "title": "DSH 1",
                    "data": data1[:10],
                    "chart_1div": chart_1(userContext["email"], 1),
                    "chart_2div": chart_2(userContext["email"], 1),
                    "chart_3div": chart_3(userContext["email"], 1),
                    "chart_4div": chart_4(userContext["email"], 1),
                }
            )
        if data2:
            dashboards.append(
                {
                    "id": 2,
                    "title": "DSH 2",
                    "data": data2[:7],
                    "chart_1div": chart_1(userContext["email"], 2),
                    "chart_2div": chart_2(userContext["email"], 2),
                    "chart_3div": chart_3(userContext["email"], 2),
                    "chart_4div": chart_4(userContext["email"], 2),
                }
            )
        if data3:
            dashboards.append(
                {
                    "id": 3,
                    "title": "DSH 3",
                    "data": data3[:9],
                    "chart_1div": chart_1(userContext["email"], 3),
                    "chart_2div": chart_2(userContext["email"], 3),
                    "chart_3div": chart_3(userContext["email"], 3),
                    "chart_4div": chart_4(userContext["email"], 3),
                }
            )

        return render(
            request,
            "private/dashboard.html",
            {
                "dashboards": dashboards,
            },
        )


def logout(request):
    # Clean cookies and redirect
    request.session.flush()
    return redirect("login")
