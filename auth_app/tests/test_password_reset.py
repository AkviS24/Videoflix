from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.test import TestCase, override_settings
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from rest_framework import status
from rest_framework.test import APIClient


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend"
)
class PasswordResetTest(TestCase):
    """Test the password reset endpoints."""

    def setUp(self):
        """Initialize the API client and test user."""

        self.client = APIClient(
            HTTP_ORIGIN="http://127.0.0.1:5500",
        )
        self.user_model = get_user_model()
        self.email = "user@example.com"
        self.password = "OldPassword123!"
        self.user = self.user_model.objects.create_user(
            username=self.email,
            email=self.email,
            password=self.password,
        )

    def test_password_reset_sends_email_for_existing_user(self):
        """Send a reset email when the email address exists."""

        response = self.client.post(
            "/api/password_reset/",
            {"email": self.email},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(self.email, mail.outbox[0].to)
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        self.assertIn(
            f"confirm_password.html?uid={uid}&token=",
            mail.outbox[0].body,
        )

    def test_password_reset_does_not_disclose_unknown_email(self):
        """Do not reveal whether an email address is registered."""

        response = self.client.post(
            "/api/password_reset/",
            {"email": "unknown@example.com"},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(len(mail.outbox), 0)

    def test_password_confirm_resets_password_with_valid_token(self):
        """Set a new password with a valid reset token."""

        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)

        response = self.client.post(
            f"/api/password_confirm/{uid}/{token}/",
            {
                "new_password": "NewSecurePassword123!",
                "confirm_password": "NewSecurePassword123!",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.user.refresh_from_db()
        self.assertTrue(
            self.user.check_password("NewSecurePassword123!"),
        )

    def test_password_confirm_rejects_mismatched_passwords(self):
        """Rejects a reset when the two passwords do not match."""

        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)

        response = self.client.post(
            f"/api/password_confirm/{uid}/{token}/",
            {
                "new_password": "NewSecurePassword123!",
                "confirm_password": "DifferentPassword123!",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.user.refresh_from_db()
        self.assertTrue(
            self.user.check_password(self.password),
        )

    def test_passowrd_confirm_rejects_invalid_token(self):
        """Reject a reset request with an invalid token."""

        uid = urlsafe_base64_encode(force_bytes(self.user.pk))

        response = self.client.post(
            f"/api/password_confirm/{uid}/invalid-token/",
            {
                "new_password": "NewSecurePassword123!",
                "confirm_password": "NewSecurePassword123!",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.user.refresh_from_db()
        self.assertTrue(
            self.user.check_password(self.password),
        )
