from django.urls import path
from .views import SignupView, LoginView, ForgotPasswordView, ConfirmEmailView, PasswordResetConfirmView, google_authenticate

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('confirm-email/<uidb64>/<token>/', ConfirmEmailView.as_view(), name='confirm_email'),
    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('google-auth/', google_authenticate, name='google_auth'),
]
