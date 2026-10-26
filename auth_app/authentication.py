from rest_framework_simplejwt.authentication import JWTAuthentication



class CookieJWTAuthentication(JWTAuthentication):
    """Authenticate request using JWTs stored in cookies."""

    def authenticate(self, request):
        """Validate the access token stored in the request cookie."""

        access_token = request.COOKIES.get("access_token")

        if not access_token:
            return None

        validated_token = self.get_validated_token(access_token)
        return self.get_user(validated_token), validated_token
