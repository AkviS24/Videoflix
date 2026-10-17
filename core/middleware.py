from urllib.parse import urlsplit

from django.conf import settings
from django.http import HttpResponseForbidden



class CsrfOriginMiddleware:
    """Validate origins for requests that can change server state."""

    def __init__(self, get_response):
        """Initialize the middleware with the next response handler."""

        self.get_response = get_response

    def __call__(self, request):
        """Validate unsafe request before passing them to the next handler."""

        if request.method in ("GET", "HEAD", "OPTIONS", "TRACE"):
            return self.get_response(request)

        origin = request.headers.get("Origin")
        referer = request.headers.get("Referer")

        if origin:
            if not self._is_allowed_origin(origin):
                return HttpResponseForbidden("Untrusted request origin.")
        elif not referer or not self._is_allowed_origin(referer):
            return HttpResponseForbidden("Missing or untrusted request origin.")

        return self.get_response(request)

    def _is_allowed_origin(self, value):
        """Check whether a URL belongs to a configured trusted origin."""

        parsed_url = urlsplit(value)

        if not parsed_url.scheme or not parsed_url.netloc:
            return False

        origin = f"{parsed_url.scheme}://{parsed_url.netloc}"

        return origin in settings.CORS_ALLOWED_ORIGINS
