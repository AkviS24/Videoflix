from django.test import SimpleTestCase, override_settings, RequestFactory
from django.http import HttpResponse

from core.middleware import CsrfOriginMiddleware

from rest_framework import status



@override_settings(
    CORS_ALLOWED_ORIGINS=[
        "http://localhost:5500",
        "http://127.0.0.1:5500",
    ]
)
class CsrfOriginMiddlewareTest(SimpleTestCase):
    """Test origin validation for unsafe HTTP requests."""

    def setUp(self):
        """Initialize the request factory and middleware."""

        self.factory = RequestFactory()
        self.middleware = CsrfOriginMiddleware(
            lambda request: HttpResponse("OK")
        )

    def test_allows_request_from_trusted_origin(self):
        """Allow requests from a configured origin."""

        request = self.factory.post(
            "/api/register/",
            HTTP_ORIGIN="http://127.0.0.1:5500",
        )

        response = self.middleware(request)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_rejects_requests_from_untrusted_origin(self):
        """Reject requests from an unconfigured origin."""

        request = self.factory.post(
            "/api/register/",
            HTTP_ORIGIN="https://example.com",
        )

        response = self.middleware(request)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_rejects_request_without_origin_or_referer(self):
        """Reject requests without an Origin or Referer header."""

        request = self.factory.post(
            "/api/register/",
        )

        response = self.middleware(request)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_allows_request_with_trusted_referer(self):
        """Allow requests with a Referer from a configured origin."""
        request = self.factory.post(
            "/api/register/",
            HTTP_REFERER="http://localhost:5500/register.html",
        )

        response = self.middleware(request)

        self.assertEqual(response.status_code, 200)

    def test_allows_safe_http_methods_without_origin(self):
        """Allow safe HTTP methods without origin headers."""
        for method in ("get", "head", "options", "trace"):
            with self.subTest(method=method):
                request = getattr(self.factory, method)("/api/register/")
                response = self.middleware(request)

                self.assertEqual(response.status_code, 200)

    def test_allows_request_from_same_origin(self):
        """Allow requests originating from the same host and port."""

        request = self.factory.post(
            "/admin/login/",
            HTTP_HOST="localhost:8000",
            HTTP_ORIGIN="http://localhost:8000",
        )

        response = self.middleware(request)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_rejects_origin_with_wrong_port(self):
        """Reject requests when the origin uses an untrusted port."""
        request = self.factory.post(
            "/api/register/",
            HTTP_ORIGIN="http://localhost:8000",
        )

        response = self.middleware(request)

        self.assertEqual(response.status_code, 403)
