from django.conf import settings
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .functions import (
    create_refresh_response,
    get_access_token,
    send_activation_email,
)
from .serializers import (
    LoginSerializer,
    RegistrationSerializer,
    PasswordResetSerializer,
    PasswordConfirmSerializer,
)



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

        token = send_activation_email(user)

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



class TokenRefreshView(APIView):
    """Refresh the access-token cookie."""

    permission_classes = []
    authentication_classes = []

    def post(self, request):
        """Validate the refresh cookie and issue a new access token."""

        raw_token = request.COOKIES.get("refresh_token")
        if not raw_token:
            return Response(
                {"detail": "Refresh token is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            access_token = get_access_token(raw_token)
        except TokenError:
            return Response(
                {"detail": "Invalid refresh token."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        return create_refresh_response(access_token)



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



class PasswordResetView(APIView):
    """Send a password reset link without disclosing account existence."""

    permission_classes = []
    authentication_classes = []

    def post(self, request):
        """Send a reset email when eligible account exists."""

        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        user_model = get_user_model()
        user = user_model.objects.filter(
            email__iexact=email,
            is_active=True,
        ).first()

        if user:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            frontend_url = (
                "http://127.0.0.1:5500/pages/auth/confirm_password.html"
            )
            reset_url = f"{frontend_url}?uid={uid}&token={token}"
            send_mail(
                subject="Reset your videoflix password.",
                message=(
                    "Use this link to reset your password:\n"
                    f"{reset_url}"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )

        return Response(
            {"detail": "If the account exists, a reset email was sent."},
            status=status.HTTP_200_OK,
        )



class PasswordConfirmView(APIView):
    """Validate a reset-token and set a new password."""

    permission_classes = []
    authentication_classes = []

    def post(self, request, uidb64, token):
        """Set a new password after validating the reset request."""

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
                {"detail": "Invalid password reset link."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not user.is_active or not default_token_generator.check_token(
            user, token
        ):
            return Response(
                {"detail": "Invalid password reset link."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = PasswordConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user.set_password(serializer.validated_data["new_password"])
        user.save(update_fields=["password"])

        return Response(
            {"detail": "Password reset successful."},
            status=status.HTTP_200_OK,
        )
