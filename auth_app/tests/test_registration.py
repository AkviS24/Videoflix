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
class RegistrationTests(TestCase):
    """Test the user registration endpoint."""

    def setUp(self):
        """Initialize the APIClient and the test data."""

        self.client = APIClient()
        self.url = "/api/register/"
        self.email = "newuser@example.com"
        self.password = "SecurePassword123!"

    def test_registration_creates_inactive_user_and_send_authentication_mail(self):
        """Create an inactive user and send an authentication email for activation."""

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
        """The registration failed if the email is already registered."""

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

    def test_activation_activates_user_with_valid_token(self):
        """Activate an inactive user with a valid token"""

        user_model = get_user_model()
        user = user_model.objects.create_user(
            username=self.email,
            email=self.email,
            password=self.password,
            is_active=False,
        )
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        activation_url = f"/api/activate/{uid}/{token}/"

        response = self.client.get(activation_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.json(),
            {"message": "Activation succeed."}
        )

        user.refresh_from_db()
        self.assertTrue(user.is_active)

    def test_activation_rejects_invalid_activation_token(self):
        """Reject the activation of an inactive user, when the token is invalid."""

        user_model = get_user_model()
        user = user_model.objects.create_user(
            username=self.email,
            email=self.email,
            password=self.password,
            is_active=False,
        )
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        activation_url = f"/api/activate/{uid}/invalid-token/"

        response = self.client.get(activation_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        user.refresh_from_db()
        self.assertFalse(user.is_active)

    def test_registration_email_contains_frontend_activation_link(self):
        """Check that the activation email links to the frontend page."""

        response = self.client.post(
            self.url,
            {
                "email": self.email,
                "password": self.password,
                "confirmed_password": self.password,
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertEqual(len(mail.outbox), 1)

        email_body = mail.outbox[0].body

        self.assertIn(
            "http://127.0.0.1:5500/pages/auth/activate.html?uid=",
            email_body,
        )
        self.assertIn("&token=", email_body)
