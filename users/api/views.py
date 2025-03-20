from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import SignupSerializer, LoginSerializer, ForgotPasswordSerializer
from django.core.mail import send_mail
from rest_framework.exceptions import ValidationError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

User = get_user_model()

class SignupView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="User Signup",
        operation_description="Create a new user account. The user will receive a confirmation email to activate their account.",
        request_body=SignupSerializer,
        responses={
            201: openapi.Response("User created successfully. Please confirm your email."),
            400: openapi.Response("Invalid input data."),
        },
    )
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.is_active = False  # Deactivate account until email is confirmed
            user.save()

            # Send confirmation email
            current_site = get_current_site(request)
            mail_subject = 'Activate your account'
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            confirmation_link = f"{current_site.domain}{reverse('confirm_email', kwargs={'uidb64': uid, 'token': token})}"
            message = render_to_string('email/confirmation_email.html', {
                'user': user,
                'confirmation_link': confirmation_link,
            })
            send_mail(mail_subject, message, 'info@umemployed.com', [user.email], fail_silently=False)

            return Response({"message": "User created successfully. Please confirm your email."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ConfirmEmailView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Confirm Email",
        operation_description="Activate a user account by confirming the email using the provided token.",
        responses={
            200: openapi.Response("Email confirmed successfully."),
            400: openapi.Response("Invalid confirmation link."),
        },
    )
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return Response({"message": "Email confirmed successfully."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid confirmation link."}, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    @swagger_auto_schema(
        operation_summary="User Login",
        operation_description="Authenticate a user and return access and refresh tokens.",
        request_body=LoginSerializer,
        responses={
            200: openapi.Response("Login successful."),
            400: openapi.Response("Invalid email or password."),
        },
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Forgot Password",
        operation_description="Send a password reset email to the user.",
        request_body=ForgotPasswordSerializer,
        responses={
            200: openapi.Response("Password reset email sent."),
            400: openapi.Response("Invalid email."),
        },
    )
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.get(email=email)

            # Send password reset email
            current_site = get_current_site(request)
            mail_subject = 'Reset your password'
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_link = f"{current_site.domain}{reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})}"
            message = render_to_string('email/password_reset_email.html', {
                'user': user,
                'reset_link': reset_link,
            })
            send_mail(mail_subject, message, 'info@umemployed.com', [user.email], fail_silently=False)

            return Response({"message": "Password reset email sent."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Reset Password",
        operation_description="Reset the user's password using the provided token and new password.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'new_password': openapi.Schema(type=openapi.TYPE_STRING, description='New password'),
                'confirm_password': openapi.Schema(type=openapi.TYPE_STRING, description='Confirm new password'),
            },
            required=['new_password', 'confirm_password'],
        ),
        responses={
            200: openapi.Response("Password has been reset successfully."),
            400: openapi.Response("Invalid or expired reset link, or passwords do not match."),
        },
    )
    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({"error": "Invalid or expired reset link."}, status=status.HTTP_400_BAD_REQUEST)

        if not default_token_generator.check_token(user, token):
            return Response({"error": "Invalid or expired reset link."}, status=status.HTTP_400_BAD_REQUEST)

        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')

        if not new_password or not confirm_password:
            raise ValidationError({"error": "Both new_password and confirm_password are required."})

        if new_password != confirm_password:
            raise ValidationError({"error": "Passwords do not match."})

        user.set_password(new_password)
        user.save()
        return Response({"message": "Password has been reset successfully."}, status=status.HTTP_200_OK)
