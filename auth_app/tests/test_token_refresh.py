from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken



class TokenRefreshTest(APITestCase):
    """Test refresh-token endpoint behavior."""

    def test_refresh_rejects_missing_cookie(self):
        """Reject a refresh request without a refresh-token cookie."""

        response = self.client.post(
            "/api/token/refresh/",
            {},
            format="json",
            HTTP_ORIGIN="http://127.0.0.1:5500",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_refresh_sets_new_access_cookie(self):
        """Issue a new access-token cookie for a valid refresh token."""

        user_model = get_user_model()
        user = user_model.objects.create_user(
            username="refresh@example.com",
            email="refresh@example.com",
            password="TestPassword123!",
        )
        refresh = RefreshToken.for_user(user)
        self.client.cookies["refresh_token"] = str(refresh)

        response = self.client.post(
            "/api/token/refresh/",
            {},
            format="json",
            HTTP_ORIGIN="http://127.0.0.1:5500",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertIn("access_token", response.cookies)
        self.assertTrue(response.cookies["access_token"].value)

    def test_refresh_rejects_invalid_token(self):
        """Reject a malformed refresh token."""

        self.client.cookies["refresh_token"] = "invalid-token"

        response = self.client.post(
            "/api/token/refresh/",
            {},
            format="json",
            HTTP_ORIGIN="http://127.0.0.1:5500",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
