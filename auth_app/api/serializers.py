from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password

from rest_framework import serializers



class RegistrationSerializer(serializers.Serializer):
    """Validate registration data and create an inactive user."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    confirmed_password = serializers.CharField(write_only=True)

    def validate_email(self, value):
        """Rejects email addresses that already registered."""

        email = value.strip().lower()
        user_model = get_user_model()

        if user_model.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError(
                "A user with this email address already exists.",
            )
        return email

    def validate(self, attrs):
        """Validate password confirmation and password strength."""

        if attrs["password"] != attrs["confirmed_password"]:
            raise serializers.ValidationError(
                {"confirmed_password": "Passwords do not match."},
            )

        validate_password(attrs["password"])
        return attrs

    def create(self, validated_data):
        """Create an inactive user with the email as username."""

        user_model = get_user_model()
        email = validated_data["email"]

        return user_model.objects.create_user(
            username=email,
            email=email,
            password=validated_data["password"],
            is_active=False,
        )



class LoginSerializer(serializers.Serializer):
    """Validate credentials and authenticate an active user."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """Authenticate the user and reject invalid credentials."""

        user = authenticate(
            request=self.context.get("request"),
            username=attrs["email"].strip().lower(),
            password=attrs["password"],
        )
        if user is None:
            raise serializers.ValidationError(
                {"detail": "Invalid email or password."},
            )

        attrs["user"] = user
        return attrs



class PasswordResetSerializer(serializers.Serializer):
    """Validate the email address for a password reset request."""

    email = serializers.EmailField()

    def validate_email(self, value):
        """Normalize the email address."""

        return value.strip().lower()


class PasswordConfirmSerializer(serializers.Serializer):
    """Validate the new password and its confirmation."""

    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """Check password confirmation and password strength."""

        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match."},
            )

        validate_password(attrs["new_password"])
        return attrs
