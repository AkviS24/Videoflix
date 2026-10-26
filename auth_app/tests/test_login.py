from django.conf import settings
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APITestCase



class LoginTests(APITestCase):
    """Test the login endpoint and the authentication cookies."""

    def setUp(self):
        """Create an active user for login tests."""

        user_model = get_user_model()
        self.email = "login@example.com"
        self.password = "SecureTestPassword123!"
        user_model.objects.create_user(
            username=self.email,
            email=self.email,
            password=self.password,
            is_active=True,
        )
        self.url = "/api/login/"

    def test_login_sets_jwt_cookies(self):
        """Return success and set both authentication cookies."""

        response = self.client.post(
            self.url,
            {
                "email": self.email,
                "password": self.password,
            },
            format="json",
            HTTP_ORIGIN="http://127.0.0.1:5500",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            response.content.decode(),
        )
        self.assertIn("access_token", response.cookies)
        self.assertIn("refresh_token", response.cookies)
        self.assertTrue(response.cookies["access_token"]["httponly"])
        self.assertTrue(response.cookies["refresh_token"]["httponly"])

    def test_login_rejects_invalid_credentials(self):
        """Reject login attempts with an incorrect password."""

        response = self.client.post(
            self.url,
            {
                "email": self.email,
                "password": "WrongPassword123!",
            },
            format="json",
            HTTP_ORIGIN="http://127.0.0.1:5500",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertNotIn("access_token", response.cookies)
        self.assertNotIn("refresh_token", response.cookies)

    def test_login_rejects_inactive_user(self):
        """Reject login attempts from inactive users."""

        user_model = get_user_model()
        user = user_model.objects.get(email=self.email)
        user.is_active = False
        user.save(update_fields=["is_active"])

        response = self.client.post(
            self.url,
            {
                "email": self.email,
                "password": self.password,
            },
            format="json",
            HTTP_ORIGIN="http://127.0.0.1:5500",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertNotIn("access_token", response.cookies)
        self.assertNotIn("refresh_token", response.cookies)

    def test_login_sets_secure_cookie_attributes(self):
        """Set the expected security attributes on login cookies."""

        response = self.client.post(
            self.url,
            {
                "email": self.email,
                "password": self.password,
            },
            format="json",
            HTTP_ORIGIN="http://127.0.0.1:5500",
        )

        for cookie_name in ("access_token", "refresh_token"):
            cookie = response.cookies[cookie_name]
            self.assertTrue(cookie["httponly"])
            self.assertEqual(cookie["samesite"], "Lax")
            self.assertEqual(cookie["secure"], not settings.DEBUG)

    def test_login_rejects_unknown_email(self):
        """Reject login attempts for an unknown email address."""

        response = self.client.post(
            self.url,
            {
                "email": "unknown@example.com",
                "password": self.password,
            },
            format="json",
            HTTP_ORIGIN="http://127.0.0.1:5500",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertNotIn("access_token", response.cookies)
        self.assertNotIn("refresh_token", response.cookies)

    def test_login_rejects_missing_credentials(self):
        """Reject login attempts when credentials are missing."""

        response = self.client.post(
            self.url,
            {
                "email": self.email,
            },
            format="json",
            HTTP_ORIGIN="http://127.0.0.1:5500",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertNotIn("access_token", response.cookies)
        self.assertNotIn("refresh_token", response.cookies)

    def test_login_rejects_missing_email(self):
        """Reject login attempts when the email is missing."""

        response = self.client.post(
            self.url,
            {
                "password": self.password,
            },
            format="json",
            HTTP_ORIGIN="http://127.0.0.1:5500",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertNotIn("access_token", response.cookies)
        self.assertNotIn("refresh_token", response.cookies)
