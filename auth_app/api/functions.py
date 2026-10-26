from django.conf import settings
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator

from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken


def send_activation_email(user):
    """Send an account activation email to the new user."""

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    frontend_url = "http://127.0.0.1:5500/pages/auth/activate.html"
    activation_url = f"{frontend_url}?uid={uid}&token={token}"

    send_mail(
        subject="Activate your Videoflix account",
        message=(
            "Thank you for registering with Videoflix.\n\n"
            f"Activate your account using this link:\n{activation_url}"
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=(
            '<h1 style="color:#e50914;">Welcome to Videoflix!</h1>'
            "<p>Thank you for registering.</p>"
            f'<p><a href="{activation_url}">'
            "Activate your account</a></p>"
        ),
        fail_silently=False,
    )
    return token


def get_access_token(raw_token):
    """Validate a refresh token and return a new access token."""

    refresh = RefreshToken(raw_token)
    return str(refresh.access_token)


def create_refresh_response(access_token):
    """Return a successful response with a new access-token cookie."""

    response = Response(
        {"detail": "Token refreshed."},
        status=status.HTTP_200_OK,
    )
    response.set_cookie(
        "access_token",
        access_token,
        httponly=True,
        secure=not settings.DEBUG,
        samesite="Lax",
    )
    return response
