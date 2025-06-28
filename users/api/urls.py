from django.urls import path
from .views import SignupView, LoginView, ForgotPasswordView, ConfirmEmailView, PasswordResetConfirmView, GoogleAuthView, ChooseAccountTypeView, ResendConfirmationEmailView, CheckEmailVerifiedView, UserInfoView, TestBackgroundProcessView, DeleteAccountView, DeleteAccountDebugView

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('confirm-email/<uidb64>/<token>/', ConfirmEmailView.as_view(), name='confirm_email'),
    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('google-auth/', GoogleAuthView.as_view(), name='google_auth'),
    path('choose-account-type/', ChooseAccountTypeView.as_view(), name='choose_account_type'),
    path('resend-confirmation-email/', ResendConfirmationEmailView.as_view(), name='resend_confirmation_email'),
    path('check-email-verified/', CheckEmailVerifiedView.as_view(), name='check_email_verified'),
    path('profile/', UserInfoView.as_view(), name='profile'),
    path('test-background-process/', TestBackgroundProcessView.as_view(), name='test_background_process'),
    path('delete-account-debug/', DeleteAccountDebugView.as_view(), name='delete_account_debug'),
    path('delete-account/', DeleteAccountView.as_view(), name='delete_account'),
]
