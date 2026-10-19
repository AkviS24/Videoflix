from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import LoginSerializer, RegistrationSerializer



class LoginView(APIView):
    """Authenticate a user and issue JWT cookies."""

    permission_classes = []
    authentication_classes = []

    def post(self, request):
        """Validate credentials and set authentication cookies."""

        serializer = LoginSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        refresh = RefreshToken.for_user(user)
        response = Response(
            {"detail": "Login successful."},
            status=status.HTTP_200_OK,
        )
        response.set_cookie(
            "access_token",
            str(refresh.access_token),
            httponly=True,
            secure=not settings.DEBUG,
            samesite="Lax",
        )
        response.set_cookie(
            "refresh_token",
            str(refresh),
            httponly=True,
            secure=not settings.DEBUG,
            samesite="Lax",
        )
        return response



class LogoutView(APIView):
    """Invalidate the refresh token and clear authentication cookies."""

    permission_classes = []
    authentication_classes = []

    def post(self, request):
        """Blacklist the refresh token and delete both cookies."""

        raw_token = request.COOKIES.get("refresh_token")
        if not raw_token:
            return Response(
                {"detail": "Refresh token is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            RefreshToken(raw_token).blacklist()
        except TokenError:
            return Response(
                {"detail": "Invalid refresh token."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        response = Response(
            {
                "detail": (
                    "Logout successful! All tokens will be deleted. "
                    "Refresh token is now invalid."
                )
            },
            status=status.HTTP_200_OK,
        )
        response.delete_cookie("access_token", samesite="Lax")
        response.delete_cookie("refresh_token", samesite="Lax")
        return response



class RegistrationView(APIView):
    """Register a new user and send an activation email."""

    permission_classes = []
    authentication_classes = []

    def post(self, request):
        """Validate registration data and create an inactive user account."""

        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        activation_path = reverse(
            "activate",
            kwargs={"uidb64": uid, "token": token},
        )
        frontend_url = "http://127.0.0.1:5500/pages/auth/activate.html"
        activation_url = f"{frontend_url}?uid={uid}&token={token}"

        send_mail(
            subject="Activate your Videoflix account",
            message=(
                "Thank you for registering with Videoflix.\n\n"
                f"Activate your account using this link:\n{activation_url}"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=(
                '<h1 style="color:#e50914;">Welcome to Videoflix!</h1>'
                "<p>Thank you for registering.</p>"
                f'<p><a href="{activation_url}">'
                "Activate your account</a></p>"
            ),
            fail_silently=False,
        )

        return Response(
            {
                "user": {
                    "id": user.pk,
                    "email": user.email,
                },
                "token": token,
            },
            status=status.HTTP_201_CREATED,
        )



class ActivationView(APIView):
    """Activate a user account by using the activation-link from email."""

    permission_classes = []
    authentication_classes = []

    def get(self, request, uidb64, token):
        """Validate the activation-token and activate the user acccount."""

        user_model = get_user_model()

        try:
            user_id = urlsafe_base64_decode(uidb64).decode()
            user = user_model.objects.get(pk=user_id)
        except(
            TypeError,
            ValueError,
            OverflowError,
            user_model.DoesNotExist,
        ):
            return Response(
                {"message": "Account activation failed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if user.is_active or not default_token_generator.check_token(
            user, token
        ):
            return Response(
                {"message": "Account activation failed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.is_active = True
        user.save(update_fields=["is_active"])

        return Response(
            {"message": "Activation succeed."},
            status=status.HTTP_200_OK,
        )
