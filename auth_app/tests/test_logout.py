from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
)
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.test import APITestCase



class LogoutTests(APITestCase):
    """Test logout behavior and refresh token invalidation."""

    def test_logout_rejects_missing_refresh_cookie(self):
        """Reject logout when the refresh token cookie is missing."""

        response = self.client.post(
            "/api/logout/",
            {},
            format="json",
            HTTP_ORIGIN="http://127.0.0.1:5500",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_logout_blacklists_refresh_token_and_deletes_cookies(self):
        """Blacklist the refresh token and delete both auth cookies."""

        user = get_user_model().objects.create_user(
            username="logout@example.com",
            email="logout@example.com",
            password="TestPassword123!",
        )
        refresh = RefreshToken.for_user(user)
        self.client.cookies["refresh_token"] = str(refresh)
        self.client.cookies["access_token"] = str(refresh.access_token)

        response = self.client.post(
            "/api/logout/",
            {},
            format="json",
            HTTP_ORIGIN="http://127.0.0.1:5500",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertTrue(
            BlacklistedToken.objects.filter(token__jti=refresh["jti"]).exists()
        )
        self.assertEqual(response.cookies["access_token"].value, "")
        self.assertEqual(response.cookies["refresh_token"].value, "")
