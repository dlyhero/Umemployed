import logging

from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.db import transaction
from django.http import HttpResponseRedirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.decorators.csrf import csrf_exempt
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from social_core.backends.google import GoogleOAuth2
from social_django.models import UserSocialAuth
from social_django.utils import load_strategy

from company.models import Company  # Import the Company model
from notifications.models import Notification
from umemployed.celery import app as celery_app  # Import your celery app

from .serializers import (
    ChangePasswordSerializer,
    ForgotPasswordSerializer,
    LoginSerializer,
    SignupSerializer,
)

User = get_user_model()
logger = logging.getLogger(__name__)


# Updated background task to send an email after a 1-minute delay
@shared_task
def test_background_task():
    import time

    time.sleep(60)  # Wait for 1 minute
    logger.warning("Celery test_background_task is running!")
    from django.core.mail import send_mail

    send_mail(
        subject="Background Task Test",
        message="This is a test email sent from the background Celery task.",
        from_email="billleynyuy@gmail.com",
        recipient_list=["billleynyuy@gmail.com"],
        fail_silently=False,
    )
    logger.warning("Celery test_background_task sent the email!")
    return "Background task completed and email sent"


# Updated background task to send an email after a 1-minute delay
@shared_task
def test_background_task():
    import time

    time.sleep(60)  # Wait for 1 minute
    logger.warning("Celery test_background_task is running!")
    from django.core.mail import send_mail

    send_mail(
        subject="Background Task Test",
        message="This is a test email sent from the background Celery task.",
        from_email="billleynyuy@gmail.com",
        recipient_list=["billleynyuy@gmail.com"],
        fail_silently=False,
    )
    logger.warning("Celery test_background_task sent the email!")
    return "Background task completed and email sent"


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
            user.is_recruiter = False  # Set is_recruiter to False
            user.is_applicant = False  # Set is_applicant to False
            user.save()

            # Send confirmation email
            mail_subject = "Activate your account"
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            confirmation_link = (
                f"https://server.umemployed.com/api/users/confirm-email/{uid}/{token}"
            )
            print(confirmation_link)
            message = render_to_string(
                "email/confirmation_email.html",
                {
                    "user": user,
                    "confirmation_link": confirmation_link,
                },
            )
            send_mail(
                mail_subject,
                "",  # Leave plain text empty
                "info@umemployed.com",
                [user.email],
                fail_silently=False,
                html_message=message,  # Send as HTML email
            )
            # Notify user of signup
            Notification.objects.create(
                user=user,
                notification_type=Notification.ACCOUNT_ALERT,
                message="Your account has been created. Please confirm your email to activate your account.",
            )

            return Response(
                {"message": "User created successfully. Please confirm your email."},
                status=status.HTTP_201_CREATED,
            )
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
            # Redirect to success URL
            success_url = "https://umemployed-front-end.vercel.app/verify_email/success"
            return HttpResponseRedirect(success_url)
        else:
            # Redirect to failure URL
            failure_url = "https://umemployed-front-end.vercel.app/verify_email/failure"
            return HttpResponseRedirect(failure_url)


@method_decorator(csrf_exempt, name="dispatch")
class LoginView(APIView):
    @swagger_auto_schema(
        operation_summary="User Login",
        operation_description="Authenticate a user and return access and refresh tokens.",
        request_body=LoginSerializer,
        responses={
            200: openapi.Response("Login successful."),
            400: openapi.Response("Invalid email or password."),
            403: openapi.Response("Email not verified."),
        },
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = User.objects.get(email=serializer.validated_data["email"])
            if not user.is_active:
                return Response({"error": "Email not verified."}, status=status.HTTP_403_FORBIDDEN)

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            # Determine role based on user attributes
            if user.is_recruiter:
                role = "recruiter"
            elif user.is_applicant:
                role = "job_seeker"
            else:
                role = None

            response_data = {
                "email": user.email,
                "role": role,
                "user_id": user.id,
                "access_token": access_token,
                "refresh_token": refresh_token,
            }

            if user.is_recruiter:
                # Query the Company model for the company ID
                company = getattr(user, "company", None)
                response_data["has_company"] = user.has_company
                response_data["company_id"] = company.id if company else None
            else:  # Job seeker
                response_data["has_resume"] = user.has_resume

            return Response(response_data, status=status.HTTP_200_OK)
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
            email = serializer.validated_data["email"]
            user = User.objects.get(email=email)

            # Send password reset email
            current_site = get_current_site(request)
            mail_subject = "Reset your password"
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_link = f"{current_site.domain}{reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})}"
            message = render_to_string(
                "email/password_reset_email.html",
                {
                    "user": user,
                    "reset_link": reset_link,
                },
            )
            send_mail(
                mail_subject, message, "info@umemployed.com", [user.email], fail_silently=False
            )

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
                "new_password": openapi.Schema(
                    type=openapi.TYPE_STRING, description="New password"
                ),
                "confirm_password": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Confirm new password"
                ),
            },
            required=["new_password", "confirm_password"],
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
            return Response(
                {"error": "Invalid or expired reset link."}, status=status.HTTP_400_BAD_REQUEST
            )

        if not default_token_generator.check_token(user, token):
            return Response(
                {"error": "Invalid or expired reset link."}, status=status.HTTP_400_BAD_REQUEST
            )

        new_password = request.data.get("new_password")
        confirm_password = request.data.get("confirm_password")

        if not new_password or not confirm_password:
            raise ValidationError({"error": "Both new_password and confirm_password are required."})

        if new_password != confirm_password:
            raise ValidationError({"error": "Passwords do not match."})

        user.set_password(new_password)
        user.save()
        return Response(
            {"message": "Password has been reset successfully."}, status=status.HTTP_200_OK
        )


@api_view(["POST"])
def google_authenticate(request):
    """
    Authenticate a user using Google ID token and return JWT tokens.
    """
    print(f"Google Auth: Incoming request data: {request.data}")
    token = request.data.get("token")
    if not token:
        print("Google Auth: No token provided in request body.")
        return Response(
            {"error": "Token is required.", "error_code": "NO_TOKEN"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    print(f"Google Auth: Received token: {token}")
    try:
        idinfo = id_token.verify_oauth2_token(
            token, google_requests.Request(), settings.GOOGLE_CLIENT_ID
        )
        email = idinfo.get("email")
        picture = idinfo.get("picture", "")  # Get picture from token
        if not email:
            return Response(
                {"error": "No email found in token."}, status=status.HTTP_400_BAD_REQUEST
            )

        # Check if the user has been deleted
        deleted_user = User.objects.filter(email=email, is_deleted=True).first()
        if deleted_user:
            return Response(
                {"error": "This account has been deleted. Please contact support."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Get or create user
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "username": email.split("@")[0],
                "first_name": idinfo.get("given_name", ""),
                "last_name": idinfo.get("family_name", ""),
                "is_active": True,
            },
        )
        if not user.is_active:
            return Response(
                {"error": "User account is inactive."}, status=status.HTTP_403_FORBIDDEN
            )
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        print(f"Google Auth: Authenticated user {user.email} (id={user.id})")
        # Determine role based on user attributes
        if user.is_recruiter:
            role = "recruiter"
        elif user.is_applicant:
            role = "job_seeker"
        else:
            role = None

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh),
                "role": role,
                "user": {
                    "email": user.email,
                    "name": user.first_name,
                    "picture": picture,
                },
            }
        )
    except Exception as e:
        print(
            f"Google Auth: Exception occurred during authentication. Token: {token}. Exception: {e}"
        )
        return Response(
            {"error": str(e), "error_code": "EXCEPTION"}, status=status.HTTP_400_BAD_REQUEST
        )


class ChooseAccountTypeView(APIView):
    """
    API endpoint to allow users to choose their account type (recruiter or job seeker).
    """

    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Choose Account Type",
        operation_description="Allows a user to select their account type (recruiter or job seeker).",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "account_type": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    enum=["recruiter", "job_seeker"],
                    description="The type of account to choose.",
                ),
            },
            required=["account_type"],
        ),
        responses={
            200: openapi.Response("Account type updated successfully."),
            400: openapi.Response("Invalid account type."),
        },
    )
    def post(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response(
                {"error": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED
            )

        account_type = request.data.get("account_type")
        if account_type == "recruiter":
            user.is_recruiter = True
            user.is_applicant = False
            subscription_user_type = "recruiter"
        elif account_type == "job_seeker":
            user.is_recruiter = False
            user.is_applicant = True
            subscription_user_type = "user"
        else:
            return Response({"error": "Invalid account type."}, status=status.HTTP_400_BAD_REQUEST)

        user.save()

        # Update or create the active subscription with the correct user_type
        from transactions.models import Subscription

        subscription = Subscription.objects.filter(user=user, is_active=True).first()
        if subscription:
            if subscription.user_type != subscription_user_type:
                subscription.user_type = subscription_user_type
                subscription.save()
        else:
            Subscription.objects.create(
                user=user, user_type=subscription_user_type, tier="basic", is_active=True
            )

        return Response(
            {
                "message": "Account type updated successfully.",
                "state": "recruiter" if user.is_recruiter else "job_seeker",
            },
            status=status.HTTP_200_OK,
        )


class ResendConfirmationEmailView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Resend Confirmation Email",
        operation_description="Resend the email confirmation link to the user.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "email": openapi.Schema(type=openapi.TYPE_STRING, description="User email"),
            },
            required=["email"],
        ),
        responses={
            200: openapi.Response("Confirmation email resent successfully."),
            400: openapi.Response("Invalid email or user already activated."),
        },
    )
    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
            if user.is_active:
                return Response(
                    {"error": "User is already activated."}, status=status.HTTP_400_BAD_REQUEST
                )

            # Resend confirmation email
            current_site = get_current_site(request)
            mail_subject = "Activate your account"
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            confirmation_link = f"https://newsite.example.com/confirm-email/{uid}/{token}"
            message = render_to_string(
                "email/confirmation_email.html",
                {
                    "user": user,
                    "confirmation_link": confirmation_link,
                },
            )
            send_mail(
                mail_subject,
                "",  # Leave plain text empty
                "info@umemployed.com",
                [user.email],
                fail_silently=False,
                html_message=message,  # Send as HTML email
            )

            return Response(
                {"message": "Confirmation email resent successfully."}, status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response(
                {"error": "User with this email does not exist."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class CheckEmailVerifiedView(APIView):
    """
    API endpoint to check if a user's email is verified.
    """

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Check Email Verification",
        operation_description="Check if the authenticated user's email is verified.",
        responses={
            200: openapi.Response("Email verification status retrieved successfully."),
        },
    )
    def get(self, request):
        return Response({"is_email_verified": request.user.is_active}, status=status.HTTP_200_OK)


class UserInfoView(APIView):
    """
    API endpoint to fetch all user information.
    """

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Fetch User Information",
        operation_description="Retrieve all information about the authenticated user.",
        responses={
            200: openapi.Response("User information retrieved successfully."),
        },
    )
    def get(self, request):
        user = request.user
        user_data = {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_recruiter": user.is_recruiter,
            "is_applicant": user.is_applicant,
            "has_resume": user.has_resume,
            "has_company": user.has_company,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
        }
        return Response(user_data, status=status.HTTP_200_OK)


class TestBackgroundProcessView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # Trigger the background task
        result = test_background_task.delay()
        return Response(
            {
                "message": "Background task triggered. An email will be sent to info@umemployed.com after 1 minute.",
                "task_id": result.id,
            },
            status=status.HTTP_202_ACCEPTED,
        )


class DeleteAccountDebugView(APIView):
    """
    Debug endpoint to check what's preventing account deletion.
    """

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Debug Account Deletion",
        operation_description="Check what related objects exist for the user account.",
        responses={
            200: openapi.Response("Debug information retrieved successfully."),
        },
    )
    def get(self, request):
        user = request.user

        debug_info = {"user_id": user.id, "user_email": user.email, "related_objects": {}}

        try:
            # Check all related objects
            debug_info["related_objects"]["resumes"] = (
                user.resume_set.count() if hasattr(user, "resume_set") else 0
            )
            debug_info["related_objects"]["skills"] = (
                user.skills.count() if hasattr(user, "skills") else 0
            )
            debug_info["related_objects"]["experiences"] = (
                user.experiences.count() if hasattr(user, "experiences") else 0
            )
            debug_info["related_objects"]["work_experiences"] = (
                user.work_experiences.count() if hasattr(user, "work_experiences") else 0
            )
            debug_info["related_objects"]["subscriptions"] = (
                user.subscriptions.count() if hasattr(user, "subscriptions") else 0
            )
            debug_info["related_objects"]["transactions"] = (
                user.transactions.count() if hasattr(user, "transactions") else 0
            )

            # Check for any custom user profile
            try:
                from resume.models import UserProfile

                debug_info["related_objects"]["user_profiles"] = UserProfile.objects.filter(
                    user=user
                ).count()
            except:
                debug_info["related_objects"]["user_profiles"] = "N/A"

            # Check for notifications
            try:
                debug_info["related_objects"]["notifications"] = (
                    user.notification_set.count() if hasattr(user, "notification_set") else 0
                )
            except:
                debug_info["related_objects"]["notifications"] = "N/A"

            # Check for company if recruiter
            try:
                debug_info["related_objects"]["companies"] = (
                    user.company_set.count() if hasattr(user, "company_set") else 0
                )
            except:
                debug_info["related_objects"]["companies"] = "N/A"

        except Exception as e:
            debug_info["error"] = str(e)

        return Response(debug_info, status=status.HTTP_200_OK)


class DeleteAccountView(APIView):
    """
    API endpoint to allow an authenticated user to delete their own account.
    """

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Delete Account",
        operation_description="Delete the authenticated user's account.",
        responses={
            204: openapi.Response("Account deleted successfully."),
            401: openapi.Response("Authentication required."),
            500: openapi.Response("Error occurred while deleting account."),
        },
    )
    def delete(self, request):
        user = request.user

        try:
            from django.db import transaction

            with transaction.atomic():
                # Log the deletion attempt
                logger.info(f"Attempting to delete user account: {user.email} (ID: {user.id})")

                # Revoke tokens for this user (multiple approaches)
                tokens_revoked = 0
                try:
                    # Approach 1: Try SimpleJWT token blacklist if available
                    try:
                        from django.apps import apps
                        from rest_framework_simplejwt.token_blacklist.models import (
                            BlacklistedToken,
                            OutstandingToken,
                        )

                        # Check if the token blacklist app is installed
                        if apps.is_installed("rest_framework_simplejwt.token_blacklist"):
                            outstanding_tokens = OutstandingToken.objects.filter(user=user)
                            for token in outstanding_tokens:
                                try:
                                    BlacklistedToken.objects.get_or_create(token=token)
                                    tokens_revoked += 1
                                except Exception as e:
                                    logger.warning(f"Could not blacklist token {token.id}: {e}")

                            if tokens_revoked > 0:
                                logger.info(
                                    f"Blacklisted {tokens_revoked} outstanding tokens for user {user.id}"
                                )
                        else:
                            logger.info(f"Token blacklist app not installed for user {user.id}")

                    except (ImportError, Exception) as e:
                        logger.info(f"Token blacklisting not available: {e}")

                    # Approach 2: Try to invalidate current refresh token if available
                    try:
                        # If the user has a current refresh token in the request
                        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
                        if auth_header.startswith("Bearer "):
                            # This won't work for access tokens, but worth logging
                            logger.info(
                                f"Current session token will be invalidated after user {user.id} deletion"
                            )
                    except Exception as e:
                        logger.debug(f"Could not process current token for user {user.id}: {e}")

                except Exception as e:
                    logger.warning(f"Error during token revocation for user {user.id}: {e}")

                # Get related objects count for logging
                related_counts = {}
                try:
                    related_counts["resumes"] = (
                        user.resume_set.count() if hasattr(user, "resume_set") else 0
                    )
                    related_counts["skills"] = user.skills.count() if hasattr(user, "skills") else 0
                    related_counts["experiences"] = (
                        user.experiences.count() if hasattr(user, "experiences") else 0
                    )
                    related_counts["work_experiences"] = (
                        user.work_experiences.count() if hasattr(user, "work_experiences") else 0
                    )
                    related_counts["subscriptions"] = (
                        user.subscriptions.count() if hasattr(user, "subscriptions") else 0
                    )
                    related_counts["transactions"] = (
                        user.transactions.count() if hasattr(user, "transactions") else 0
                    )

                    logger.info(f"User {user.id} has related objects: {related_counts}")
                except Exception as e:
                    logger.warning(f"Could not count related objects for user {user.id}: {e}")

                # Soft delete the user instead of hard deleting
                from django.utils import timezone

                user_email = user.email
                user_id = user.id

                # Update the user to mark as deleted
                user.is_deleted = True
                user.deleted_at = timezone.now()
                user.is_active = False  # Prevents login

                # Anonymize personal data for privacy
                user.first_name = "Deleted"
                user.last_name = "User"
                # Keep the email but mark it as deleted to prevent reuse
                if not user.email.startswith("deleted_"):
                    user.email = f"deleted_{user.id}_{user.email}"

                user.save()

                logger.info(f"Successfully soft-deleted user account: {user_email} (ID: {user_id})")

                return Response(
                    {
                        "message": "Account deleted successfully.",
                        "deleted_user_id": user_id,
                        "deleted_user_email": user_email,
                        "tokens_revoked": tokens_revoked,
                        "related_objects_deleted": related_counts,
                    },
                    status=status.HTTP_204_NO_CONTENT,
                )

        except Exception as e:
            logger.error(f"Error deleting user account {user.id}: {str(e)}", exc_info=True)

            # Return detailed error information for debugging
            error_details = {
                "message": "An error occurred while deleting your account.",
                "error": str(e),
                "user_id": user.id,
            }

            # In production, you might want to hide detailed error info
            if hasattr(settings, "DEBUG") and not settings.DEBUG:
                error_details = {
                    "message": "An error occurred while deleting your account. Please contact support.",
                    "error_code": "DELETE_FAILED",
                }

            return Response(error_details, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ChangePasswordView(APIView):
    """
    API endpoint to allow an authenticated user to change their password.
    """

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Change Password",
        operation_description="Change the authenticated user's password by providing the current password and new password.",
        request_body=ChangePasswordSerializer,
        responses={
            200: openapi.Response("Password changed successfully."),
            400: openapi.Response("Invalid input data or current password is incorrect."),
            401: openapi.Response("Authentication required."),
        },
    )
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            # Set the new password
            user = request.user
            user.set_password(serializer.validated_data["new_password"])
            user.save()

            # Return success response
            return Response(
                {
                    "message": "Password changed successfully. Please login again with your new password."
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GoogleAuthView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get("token")
        email = request.data.get("email")
        name = request.data.get("name")
        picture = request.data.get("picture")

        if not token or not email:
            return Response({"error": "Token and email are required."}, status=400)

        try:
            # Validate Google token
            idinfo = id_token.verify_oauth2_token(token, google_requests.Request())
            if idinfo["email"] != email:
                return Response({"error": "Email mismatch"}, status=400)
        except Exception as e:
            logger.error(f"Google token validation failed: {e}")
            return Response({"error": "Invalid token"}, status=400)

        # Check if the user has been deleted
        deleted_user = User.objects.filter(email=email, is_deleted=True).first()
        if deleted_user:
            return Response(
                {"error": "This account has been deleted. Please contact support."},
                status=status.HTTP_403_FORBIDDEN,
            )

        user, created = User.objects.get_or_create(
            email=email, defaults={"username": email, "first_name": name}
        )
        # Optionally update name/picture here
        if not created:
            if name and user.first_name != name:
                user.first_name = name
                user.save()
        # You can also store/update the picture if your User model supports it

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh),
                "role": getattr(user, "role", "user"),
                "user": {
                    "email": user.email,
                    "name": user.first_name,
                    "picture": picture,
                },
            }
        )
