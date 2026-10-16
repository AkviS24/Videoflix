from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase, override_settings

from rest_framework import status
from rest_framework.test import APIClient


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend"
)
class RegistrationTests(TestCase):
    """Test the user registration endpoint."""

    def setUp(self):
        """Initialize the APIClient and the test data."""

        self.client = APIClient()
        self.url = "/api/register/"
        self.email = "newuser@exampl.com"
        self.password = "SecurePassword123!"

    def test_registration_creates_inactive_user_and_send_authentification_mail(self):
        """Create a inactive user and send a authentification mail for activation."""

        response = self.client.post(
            self.url,
            {
                "email": self.email,
                "password": self.password,
                "confirmed_password": self.password,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        user = get_user_model().objects.get(email=self.email)

        self.assertFalse(user.is_active)
        self.assertTrue(user.check_password(self.password))
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(self.email, mail.outbox[0].to)

    def test_registration_reject_mismatched_passwords(self):
        """The registration failed if password and confirmed_password don't match."""

        response = self.client.post(
            self.url,
            {
                "email": self.email,
                "password": self.password,
                "confirmed_password": "DifferentPassword123!",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertFalse(
            get_user_model().objects.filter(email=self.email).exists()
        )

    def test_registration_rejects_existing_email(self):
        """The registration failed if the email is already registert."""

        user_model = get_user_model()
        user_model.objects.create_user(
            username="existing-user",
            email=self.email,
            password=self.password,
        )

        response = self.client.post(
            self.url,
            {
                "email": self.email,
                "password": self.password,
                "confirmed_password": self.password,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertEqual(
            user_model.objects.filter(email=self.email).count(),
            1,
        )