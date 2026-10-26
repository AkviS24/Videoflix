from django.urls import path

from .views import (
    ActivationView,
    LoginView,
    LogoutView,
    PasswordConfirmView,
    PasswordResetView,
    RegistrationView,
    TokenRefreshView,
)


urlpatterns = [
    path("register/", RegistrationView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("password_reset/", PasswordResetView.as_view(), name="password_reset"),
    path(
        "password_confirm/<uidb64>/<token>/",
        PasswordConfirmView.as_view(),
        name="password_confirm",
    ),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("activate/<uidb64>/<token>/", ActivationView.as_view(), name="activate"),
]
