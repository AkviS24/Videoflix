from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from rest_framework import serializers



class RegistrationSerializer(serializers.Serializer):
    """Validate registration data and create an inactive user."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    confirmed_password = serializers.CharField(write_only=True)

    def validate_email(self, value):
        """Rejects email adresses that already registered."""

        email = value.strip().lower()
        user_model = get_user_model()

        if user_model.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError(
                "A user with this email adress already exists.",
            )
        return email

    def validate(self, attrs):
        """Validate password confirmation and password strength."""

        if attrs["password"] != attrs["confirmed_password"]:
            raise serializers.ValidationError(
                {"confirmed_password": "Password do not match."},
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