import jwt
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect
from functools import wraps
from datetime import datetime
import jwt


def check_token_validity(jwt_token):
    try:
        # Set your secret key used for signing the token
        secret_key = settings.SECRET_KEY

        # Decode the token to get its payload
        payload = jwt.decode(jwt_token, secret_key, algorithms=["HS256"])

        # Check if the token has expired
        current_time = datetime.utcnow()
        expiration_time = datetime.fromtimestamp(payload["exp"])

        if current_time > expiration_time:
            # Token has expired
            return False

        # Token is valid
        return True

    except jwt.ExpiredSignatureError:
        # Token has expired
        return False

    except (jwt.DecodeError, jwt.InvalidTokenError):
        # Invalid token
        return False


def session_auth_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if "jwt_token" not in request.session:
            return redirect("login")

        token = request.session["jwt_token"]

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            # Aquí puedes realizar las verificaciones adicionales necesarias, como validar la validez del token o comprobar los permisos del usuario.
        except jwt.DecodeError:
            return JsonResponse({"error": "Invalid token"}, status=401)

        return view_func(request, *args, **kwargs)

    return wrapper


def session_auth_not_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        jwt_token = request.session.get("jwt_token")
        if jwt_token:
            if not check_token_validity(jwt_token):
                return redirect("dashboard")

        return view_func(request, *args, **kwargs)

    return wrapper
