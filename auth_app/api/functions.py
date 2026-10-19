from django.conf import settings

from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken



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