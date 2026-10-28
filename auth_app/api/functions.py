from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator

from email.mime.image import MIMEImage
from pathlib import Path

from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken


def send_activation_email(user):
    """Send an account activation email to the new user."""

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    frontend_url = "http://127.0.0.1:5500/pages/auth/activate.html"
    activation_url = f"{frontend_url}?uid={uid}&token={token}"
    name_to_greet = user.email.split("@")[0]

    html_content = render_to_string(
        "emails/activation_email.html",
        {
            "activation_url": activation_url,
            "name_to_greet": name_to_greet,
        },
    )
    email = EmailMultiAlternatives(
        subject="Activate your Videoflix account",
        body=(
            "Thank you for registering with Videoflix.\n\n"
            f"Activate your account using this link:\n{activation_url}"
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )
    email.attach_alternative(html_content, "text/html")
    logo_path = (
        settings.BASE_DIR
        / "auth_app"
        / "static"
        / "auth_app"
        / "emails"
        / "images"
        / "Logo.png"
    )

    with open(logo_path, "rb") as logo_file:
        logo = MIMEImage(logo_file.read(), _subtype="png")

    logo.add_header("Content-ID", "<videoflix-logo>")
    logo.add_header(
        "Content-Disposition",
        "inline",
        filename="Logo.png",
    )
    email.attach(logo)
    email.send()
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
