import os
import uuid

import stripe
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from notifications.models import Notification
from transactions.models import Subscription, Transaction
from users.models import User

stripe.api_key = settings.STRIPE_SECRET_KEY


class PayPalPaymentAPIView(APIView):
    """
    API view to initiate a PayPal payment.
    """

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Initiate a PayPal payment",
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "payment_url": openapi.Schema(
                        type=openapi.TYPE_STRING, description="URL to redirect for PayPal payment"
                    ),
                },
            ),
            400: "Bad Request",
        },
    )
    def post(self, request, candidate_id):
        """
        Handle POST requests to initiate a PayPal payment.
        """
        candidate = get_object_or_404(User, id=candidate_id)
        transaction_id = str(uuid.uuid4())

        # Create a transaction
        Transaction.objects.create(
            user=request.user,
            candidate=candidate,
            transaction_id=transaction_id,
            amount=5.00,
            payment_method="paypal",
            status="pending",
        )
        print("Transaction created for user:", request.user.id)
        # Notify candidate of payment initiation for endorsements
        Notification.objects.create(
            user=candidate,
            notification_type=Notification.SPECIAL_OFFER,
            message=f"{request.user.get_full_name() or request.user.username} has initiated a payment to view your endorsements.",
        )

        # Generate PayPal payment URL
        payment_url = f"https://www.paypal.com/cgi-bin/webscr?cmd=_xclick&business={settings.PAYPAL_RECEIVER_EMAIL}&amount=5.00&item_name=Endorsements&invoice={transaction_id}&currency_code=USD&return={request.build_absolute_uri('/transactions/success/')}&cancel_return={request.build_absolute_uri('/transactions/cancel/')}"
        return Response({"payment_url": payment_url}, status=status.HTTP_200_OK)


class StripePaymentAPIView(APIView):
    """
    API view to initiate a Stripe payment.
    """

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Initiate a Stripe payment",
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "session_id": openapi.Schema(
                        type=openapi.TYPE_STRING, description="Stripe session ID"
                    ),
                },
            ),
            400: "Bad Request",
        },
    )
    def post(self, request, candidate_id):
        """
        Handle POST requests to initiate a Stripe payment.
        """
        candidate = get_object_or_404(User, id=candidate_id)
        amount = 500  # Amount in cents ($5.00)

        # Create Stripe Checkout Session
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {"name": "Endorsements"},
                        "unit_amount": amount,
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url=request.build_absolute_uri("/transactions/success/"),
            cancel_url=request.build_absolute_uri("/transactions/cancel/"),
        )

        # Create a transaction
        Transaction.objects.create(
            user=request.user,
            candidate=candidate,
            transaction_id=session.id,
            amount=amount / 100,  # Convert cents to dollars
            payment_method="stripe",
            status="pending",
        )
        # Notify candidate of payment initiation for endorsements
        Notification.objects.create(
            user=candidate,
            notification_type=Notification.SPECIAL_OFFER,
            message=f"{request.user.get_full_name() or request.user.username} has initiated a payment to view your endorsements.",
        )

        return Response({"session_id": session.id}, status=status.HTTP_200_OK)


class CreateStripeSubscriptionAPIView(APIView):
    """
    API view to create a Stripe subscription for a user or recruiter.
    """

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Create a Stripe subscription",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "tier": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Subscription tier (basic, standard, premium, custom)",
                ),
                "user_type": openapi.Schema(
                    type=openapi.TYPE_STRING, description="user or recruiter"
                ),
            },
            required=["tier", "user_type"],
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "session_id": openapi.Schema(
                        type=openapi.TYPE_STRING, description="Stripe session ID"
                    ),
                },
            ),
            400: "Bad Request",
        },
    )
    def post(self, request):
        user = request.user
        tier = request.data.get("tier")
        user_type = request.data.get("user_type")
        STRIPE_PRICE_IDS = {
            ("user", "standard"): "price_1RUpqCGhd6oP7C9j40K7Wk8J",
            ("user", "premium"): "price_1RUq6wGhd6oP7C9jLts6eQsf",
            ("recruiter", "standard"): "price_1RUpqCGhd6oP7C9j40K7Wk8J",
            ("recruiter", "premium"): "price_1RUq6wGhd6oP7C9jLts6eQsf",
            # Add more as needed
        }
        price_id = STRIPE_PRICE_IDS.get((user_type, tier))
        if not price_id:
            return Response(
                {"error": "Invalid tier or user_type."}, status=status.HTTP_400_BAD_REQUEST
            )

        # Fetch price amount from Stripe
        price_obj = stripe.Price.retrieve(price_id)
        amount = price_obj["unit_amount"] / 100 if price_obj["currency"] == "usd" else 0

        # Get frontend base URL from environment variable
        frontend_base_url = os.getenv(
            "FRONTEND_BASE_URL", "http://localhost:3000"
        )  # fallback to local dev
        # Create Stripe Checkout Session for subscription
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price": price_id,  # Use the mapped price_id based on plan
                    "quantity": 1,
                },
            ],
            mode="subscription",
            customer_email=user.email,
            success_url=f"{frontend_base_url}/pricing/success",
            cancel_url=f"{frontend_base_url}/pricing/failure",
        )

        # Optionally, mark any previous subscriptions inactive
        Subscription.objects.filter(user=user, user_type=user_type, is_active=True).update(
            is_active=False
        )

        # Create a pending subscription (will be activated on webhook)
        Subscription.objects.create(
            user=user,
            user_type=user_type,
            tier=tier,
            is_active=False,
            stripe_subscription_id=session.id,  # Temporarily store session ID, update later
        )

        # Store the actual subscription price in the transaction
        Transaction.objects.create(
            user=user,
            candidate=None,  # No candidate for subscription transactions
            transaction_id=session.id,
            amount=amount,
            payment_method="stripe",
            status="pending",
            description=f"Stripe subscription ({user_type}, {tier})",
        )

        # Notify user of subscription initiation
        Notification.objects.create(
            user=user,
            notification_type=Notification.SPECIAL_OFFER,
            message=f"Your {user_type} subscription ({tier}) process has started. Please complete payment to activate.",
        )
        return Response({"session_id": session.id}, status=status.HTTP_200_OK)


class CancelStripeSubscriptionAPIView(APIView):
    """
    API view to cancel an active Stripe subscription.
    """

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Cancel an active Stripe subscription",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "user_type": openapi.Schema(
                    type=openapi.TYPE_STRING, description="user or recruiter"
                ),
            },
            required=["user_type"],
        ),
        responses={200: "Subscription canceled"},
    )
    def post(self, request):
        user = request.user
        user_type = request.data.get("user_type")
        subscription = Subscription.objects.filter(
            user=user, user_type=user_type, is_active=True
        ).first()
        if not subscription or not subscription.stripe_subscription_id:
            return Response(
                {"error": "No active Stripe subscription found."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            # Retrieve the Stripe subscription ID from the session or update logic as needed
            stripe_sub = stripe.Subscription.retrieve(subscription.stripe_subscription_id)
            stripe.Subscription.delete(stripe_sub.id)
            subscription.is_active = False
            subscription.ended_at = timezone.now()
            subscription.save()
            return Response({"message": "Subscription canceled."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookAPIView(APIView):
    """
    API view to handle Stripe webhooks for subscription events.
    """

    authentication_classes = []  # Stripe does not send auth headers
    permission_classes = []

    def post(self, request):
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

        # Check for thin payload and fetch full event if needed
        payload_type = None
        if sig_header:
            for part in sig_header.split(","):
                if part.strip().startswith("payloadType="):
                    payload_type = part.split("=")[1]
                    break

        try:
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
            # If thin payload, fetch full event from Stripe
            if payload_type == "thin":
                event_id = event["id"]
                event = stripe.Event.retrieve(event_id)
        except (ValueError, stripe.error.SignatureVerificationError):
            return Response(status=400)

        # Handle subscription events
        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            # Find the pending subscription and activate it
            sub = Subscription.objects.filter(stripe_subscription_id=session["id"]).first()
            if sub:
                sub.is_active = True
                sub.stripe_subscription_id = session.get(
                    "subscription"
                )  # Update to real subscription ID
                sub.started_at = timezone.now()
                sub.ended_at = None
                sub.save()

                # Mark the transaction as completed
                transaction = Transaction.objects.filter(transaction_id=session["id"]).first()
                if transaction:
                    transaction.status = "completed"
                    transaction.save()
        elif event["type"] == "customer.subscription.deleted":
            subscription_obj = event["data"]["object"]
            sub = Subscription.objects.filter(stripe_subscription_id=subscription_obj["id"]).first()
            if sub:
                sub.is_active = False
                sub.ended_at = timezone.now()
                sub.save()
        # Add more event types as needed

        return Response(status=200)


class TransactionHistoryAPIView(APIView):
    """
    API view to retrieve the transaction history for the authenticated user.
    """

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve transaction history",
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "transaction_id": openapi.Schema(
                            type=openapi.TYPE_STRING, description="Transaction ID"
                        ),
                        "amount": openapi.Schema(
                            type=openapi.TYPE_NUMBER, description="Transaction amount"
                        ),
                        "payment_method": openapi.Schema(
                            type=openapi.TYPE_STRING, description="Payment method"
                        ),
                        "status": openapi.Schema(
                            type=openapi.TYPE_STRING, description="Transaction status"
                        ),
                        "created_at": openapi.Schema(
                            type=openapi.TYPE_STRING, description="Transaction creation date"
                        ),
                        "description": openapi.Schema(
                            type=openapi.TYPE_STRING, description="Transaction description"
                        ),
                        "candidate": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            description="Candidate info",
                            properties={
                                "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                "username": openapi.Schema(type=openapi.TYPE_STRING),
                                "full_name": openapi.Schema(type=openapi.TYPE_STRING),
                            },
                        ),
                    },
                ),
            ),
        },
    )
    def get(self, request):
        """
        Handle GET requests to retrieve transaction history.
        """
        transactions = (
            Transaction.objects.filter(user=request.user)
            .select_related("candidate")
            .order_by("-created_at")
        )
        data = []
        for transaction in transactions:
            candidate_info = None
            if transaction.candidate:
                candidate_info = {
                    "id": transaction.candidate.id,
                    "username": transaction.candidate.username,
                    "full_name": transaction.candidate.get_full_name()
                    or transaction.candidate.username,
                }
            data.append(
                {
                    "transaction_id": transaction.transaction_id,
                    "amount": transaction.amount,
                    "payment_method": transaction.payment_method,
                    "status": transaction.status,
                    "created_at": transaction.created_at,
                    "description": getattr(transaction, "description", ""),
                    "candidate": candidate_info,
                }
            )
        return Response(data, status=status.HTTP_200_OK)


class PaymentSuccessAPIView(APIView):
    """
    API view to handle successful payments.
    """

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Handle successful payments",
        responses={200: "Payment success acknowledged"},
    )
    def get(self, request):
        """
        Handle GET requests for successful payments.
        """
        transaction_id = request.session.get("transaction_id")
        if not transaction_id:
            return Response(
                {"error": "Transaction ID not found in session"}, status=status.HTTP_400_BAD_REQUEST
            )

        transaction = get_object_or_404(Transaction, transaction_id=transaction_id)
        transaction.status = "completed"
        transaction.save()

        return Response({"message": "Payment successful"}, status=status.HTTP_200_OK)


class PaymentCancelAPIView(APIView):
    """
    API view to handle canceled payments.
    """

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Handle canceled payments",
        responses={200: "Payment cancellation acknowledged"},
    )
    def get(self, request):
        """
        Handle GET requests for canceled payments.
        """
        transaction_id = request.session.get("transaction_id")
        if not transaction_id:
            return Response(
                {"error": "Transaction ID not found in session"}, status=status.HTTP_400_BAD_REQUEST
            )

        transaction = get_object_or_404(Transaction, transaction_id=transaction_id)
        transaction.status = "failed"
        transaction.save()

        return Response({"message": "Payment canceled"}, status=status.HTTP_200_OK)


class SubscriptionStatusAPIView(APIView):
    """
    API view to get a user's active subscription status by user ID.
    """

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get a user's active subscription status by user ID",
        manual_parameters=[
            openapi.Parameter(
                "user_id", openapi.IN_PATH, description="User ID", type=openapi.TYPE_INTEGER
            )
        ],
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "has_active_subscription": openapi.Schema(
                        type=openapi.TYPE_BOOLEAN,
                        description="Whether the user has an active subscription",
                    ),
                    "user_type": openapi.Schema(type=openapi.TYPE_STRING, description="User type"),
                    "tier": openapi.Schema(
                        type=openapi.TYPE_STRING, description="Subscription tier"
                    ),
                    "started_at": openapi.Schema(
                        type=openapi.TYPE_STRING, description="Subscription start date"
                    ),
                    "ended_at": openapi.Schema(
                        type=openapi.TYPE_STRING, description="Subscription end date"
                    ),
                },
            ),
            404: "No active subscription found",
        },
    )
    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        subscription = (
            Subscription.objects.filter(user=user, is_active=True).order_by("-started_at").first()
        )
        if not subscription:
            return Response({"has_active_subscription": False}, status=status.HTTP_200_OK)
        return Response(
            {
                "has_active_subscription": True,
                "user_type": subscription.user_type,
                "tier": subscription.tier,
                "started_at": subscription.started_at,
                "ended_at": subscription.ended_at,
            },
            status=status.HTTP_200_OK,
        )


class CreateEndorsementSubscriptionAPIView(APIView):
    """
    API view to create a Stripe subscription for endorsements.
    """

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Create a Stripe subscription for endorsements",
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "session_id": openapi.Schema(
                        type=openapi.TYPE_STRING, description="Stripe session ID"
                    ),
                },
            ),
            400: "Bad Request",
        },
    )
    def post(self, request):
        user = request.user
        ENDORSEMENT_PRICE_ID = "price_1RWu3pGhd6oP7C9jKnDDOb1o"
        frontend_base_url = os.getenv("FRONTEND_BASE_URL", "http://localhost:3000")
        # Fetch price amount from Stripe
        price_obj = stripe.Price.retrieve(ENDORSEMENT_PRICE_ID)
        amount = price_obj["unit_amount"] / 100 if price_obj["currency"] == "usd" else 0

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price": ENDORSEMENT_PRICE_ID,
                    "quantity": 1,
                },
            ],
            mode="subscription",
            customer_email=user.email,
            success_url=f"{frontend_base_url}/endorsement/success",
            cancel_url=f"{frontend_base_url}/endorsement/failure",
        )

        # Optionally, mark any previous endorsement subscriptions inactive
        Subscription.objects.filter(
            user=user, user_type="user", tier="endorsement", is_active=True
        ).update(is_active=False)
        Subscription.objects.create(
            user=user,
            user_type="user",
            tier="endorsement",
            is_active=False,
            stripe_subscription_id=session.id,
        )

        Transaction.objects.create(
            user=user,
            candidate=None,  # No candidate for subscription transactions
            transaction_id=session.id,
            amount=amount,
            payment_method="stripe",
            status="pending",
            description="Stripe endorsement subscription",
        )

        Notification.objects.create(
            user=user,
            notification_type=Notification.SPECIAL_OFFER,
            message="Your endorsement subscription process has started. Please complete payment to activate.",
        )
        return Response({"session_id": session.id}, status=status.HTTP_200_OK)


class EndorsementSubscriptionStatusAPIView(APIView):
    """
    API view to check if the user has an active endorsement subscription.
    """

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Check if the user has an active endorsement subscription",
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "has_active_endorsement_subscription": openapi.Schema(
                        type=openapi.TYPE_BOOLEAN
                    ),
                    "started_at": openapi.Schema(
                        type=openapi.TYPE_STRING, description="Subscription start date"
                    ),
                    "ended_at": openapi.Schema(
                        type=openapi.TYPE_STRING, description="Subscription end date"
                    ),
                },
            )
        },
    )
    def get(self, request):
        user = request.user
        sub = (
            Subscription.objects.filter(
                user=user, user_type="user", tier="endorsement", is_active=True
            )
            .order_by("-started_at")
            .first()
        )
        if not sub:
            return Response(
                {"has_active_endorsement_subscription": False}, status=status.HTTP_200_OK
            )
        return Response(
            {
                "has_active_endorsement_subscription": True,
                "started_at": sub.started_at,
                "ended_at": sub.ended_at,
            },
            status=status.HTTP_200_OK,
        )


class SubscriptionDebugAPIView(APIView):
    """
    Debug endpoint to check user's subscription status and permissions.
    Useful for troubleshooting job creation permission issues.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # Get all subscriptions for the user
        all_subscriptions = Subscription.objects.filter(user=user).order_by('-started_at')
        
        # Get active subscription
        active_subscription = Subscription.objects.filter(
            user=user, is_active=True
        ).order_by('-started_at').first()
        
        # Get active recruiter subscription specifically
        active_recruiter_subscription = Subscription.objects.filter(
            user=user, user_type="recruiter", is_active=True
        ).order_by('-started_at').first()
        
        # Check permissions for job creation
        can_create_jobs = bool(active_recruiter_subscription)
        job_creation_limit = None
        job_creation_usage = 0
        
        if active_recruiter_subscription:
            can_perform_posting = active_recruiter_subscription.can_perform_action("posting")
            job_creation_limit = active_recruiter_subscription.get_daily_limit()
            
            # Get today's usage
            from transactions.models import DailyUsage
            today = timezone.now().date()
            usage = DailyUsage.objects.filter(
                user=user, date=today, usage_type="posting"
            ).first()
            if usage:
                job_creation_usage = usage.count
        else:
            can_perform_posting = False
        
        response_data = {
            "user_id": user.id,
            "user_email": user.email,
            "total_subscriptions": all_subscriptions.count(),
            "active_subscription": {
                "exists": bool(active_subscription),
                "user_type": active_subscription.user_type if active_subscription else None,
                "tier": active_subscription.tier if active_subscription else None,
                "is_active": active_subscription.is_active if active_subscription else None,
                "started_at": active_subscription.started_at if active_subscription else None,
            },
            "recruiter_subscription": {
                "exists": bool(active_recruiter_subscription),
                "tier": active_recruiter_subscription.tier if active_recruiter_subscription else None,
                "is_active": active_recruiter_subscription.is_active if active_recruiter_subscription else None,
                "started_at": active_recruiter_subscription.started_at if active_recruiter_subscription else None,
            },
            "permissions": {
                "can_create_jobs": can_create_jobs,
                "can_perform_posting_action": can_perform_posting,
                "job_creation_daily_limit": job_creation_limit,
                "job_creation_usage_today": job_creation_usage,
                "jobs_remaining_today": job_creation_limit - job_creation_usage if job_creation_limit else "unlimited",
            },
            "all_subscriptions": [
                {
                    "id": sub.id,
                    "user_type": sub.user_type,
                    "tier": sub.tier,
                    "is_active": sub.is_active,
                    "started_at": sub.started_at,
                    "ended_at": sub.ended_at,
                }
                for sub in all_subscriptions
            ],
            "troubleshooting": {
                "missing_recruiter_subscription": not bool(active_recruiter_subscription),
                "subscription_inactive": active_subscription and not active_subscription.is_active if active_subscription else False,
                "wrong_user_type": active_subscription and active_subscription.user_type != "recruiter" if active_subscription else False,
                "reached_daily_limit": not can_perform_posting if active_recruiter_subscription else False,
            }
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
