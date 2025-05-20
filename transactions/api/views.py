from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from transactions.models import Transaction, Subscription
from users.models import User
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import stripe
from django.conf import settings
import uuid
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils import timezone

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
                    "payment_url": openapi.Schema(type=openapi.TYPE_STRING, description="URL to redirect for PayPal payment"),
                },
            ),
            400: "Bad Request"
        }
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
            amount=5.00,  # Example amount
            payment_method='paypal',
            status='pending',
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
                    "session_id": openapi.Schema(type=openapi.TYPE_STRING, description="Stripe session ID"),
                },
            ),
            400: "Bad Request"
        }
    )
    def post(self, request, candidate_id):
        """
        Handle POST requests to initiate a Stripe payment.
        """
        candidate = get_object_or_404(User, id=candidate_id)
        amount = 500  # Amount in cents ($5.00)

        # Create Stripe Checkout Session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {'name': 'Endorsements'},
                    'unit_amount': amount,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.build_absolute_uri('/transactions/success/'),
            cancel_url=request.build_absolute_uri('/transactions/cancel/'),
        )

        # Create a transaction
        Transaction.objects.create(
            user=request.user,
            candidate=candidate,
            transaction_id=session.id,
            amount=amount / 100,  # Convert cents to dollars
            payment_method='stripe',
            status='pending',
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
                "tier": openapi.Schema(type=openapi.TYPE_STRING, description="Subscription tier (basic, standard, premium, custom)"),
                "user_type": openapi.Schema(type=openapi.TYPE_STRING, description="user or recruiter"),
            },
            required=["tier", "user_type"]
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "session_id": openapi.Schema(type=openapi.TYPE_STRING, description="Stripe session ID"),
                },
            ),
            400: "Bad Request"
        }
    )
    def post(self, request):
        user = request.user
        tier = request.data.get("tier")
        user_type = request.data.get("user_type")
        # Map your tier/user_type to Stripe price IDs
        STRIPE_PRICE_IDS = {
            ("user", "standard"): "price_user_standard",
            ("user", "premium"): "price_user_premium",
            ("recruiter", "standard"): "price_recruiter_standard",
            ("recruiter", "premium"): "price_recruiter_premium",
            # Add more as needed
        }
        price_id = STRIPE_PRICE_IDS.get((user_type, tier))
        if not price_id:
            return Response({"error": "Invalid tier or user_type."}, status=status.HTTP_400_BAD_REQUEST)

        # Create Stripe Checkout Session for subscription
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode='subscription',
            customer_email=user.email,
            success_url=request.build_absolute_uri('/transactions/payment-success/'),
            cancel_url=request.build_absolute_uri('/transactions/payment-cancel/'),
        )

        # Optionally, mark any previous subscriptions inactive
        Subscription.objects.filter(user=user, user_type=user_type, is_active=True).update(is_active=False)

        # Create a pending subscription (will be activated on webhook)
        Subscription.objects.create(
            user=user,
            user_type=user_type,
            tier=tier,
            is_active=False,
            stripe_subscription_id=session.id  # Temporarily store session ID, update later
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
                "user_type": openapi.Schema(type=openapi.TYPE_STRING, description="user or recruiter"),
            },
            required=["user_type"]
        ),
        responses={200: "Subscription canceled"}
    )
    def post(self, request):
        user = request.user
        user_type = request.data.get("user_type")
        subscription = Subscription.objects.filter(user=user, user_type=user_type, is_active=True).first()
        if not subscription or not subscription.stripe_subscription_id:
            return Response({"error": "No active Stripe subscription found."}, status=status.HTTP_400_BAD_REQUEST)
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


@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookAPIView(APIView):
    """
    API view to handle Stripe webhooks for subscription events.
    """
    authentication_classes = []  # Stripe does not send auth headers
    permission_classes = []

    def post(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except (ValueError, stripe.error.SignatureVerificationError):
            return Response(status=400)

        # Handle subscription events
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            # Find the pending subscription and activate it
            sub = Subscription.objects.filter(stripe_subscription_id=session['id']).first()
            if sub:
                sub.is_active = True
                sub.stripe_subscription_id = session.get('subscription')  # Update to real subscription ID
                sub.started_at = timezone.now()
                sub.ended_at = None
                sub.save()
        elif event['type'] == 'customer.subscription.deleted':
            subscription_obj = event['data']['object']
            sub = Subscription.objects.filter(stripe_subscription_id=subscription_obj['id']).first()
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
                        "transaction_id": openapi.Schema(type=openapi.TYPE_STRING, description="Transaction ID"),
                        "amount": openapi.Schema(type=openapi.TYPE_NUMBER, description="Transaction amount"),
                        "payment_method": openapi.Schema(type=openapi.TYPE_STRING, description="Payment method"),
                        "status": openapi.Schema(type=openapi.TYPE_STRING, description="Transaction status"),
                        "created_at": openapi.Schema(type=openapi.TYPE_STRING, description="Transaction creation date"),
                    },
                ),
            ),
        }
    )
    def get(self, request):
        """
        Handle GET requests to retrieve transaction history.
        """
        transactions = Transaction.objects.filter(user=request.user).order_by('-created_at')
        data = [
            {
                "transaction_id": transaction.transaction_id,
                "amount": transaction.amount,
                "payment_method": transaction.payment_method,
                "status": transaction.status,
                "created_at": transaction.created_at,
            }
            for transaction in transactions
        ]
        return Response(data, status=status.HTTP_200_OK)


class PaymentSuccessAPIView(APIView):
    """
    API view to handle successful payments.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Handle successful payments",
        responses={200: "Payment success acknowledged"}
    )
    def get(self, request):
        """
        Handle GET requests for successful payments.
        """
        transaction_id = request.session.get('transaction_id')
        if not transaction_id:
            return Response({"error": "Transaction ID not found in session"}, status=status.HTTP_400_BAD_REQUEST)

        transaction = get_object_or_404(Transaction, transaction_id=transaction_id)
        transaction.status = 'completed'
        transaction.save()

        return Response({"message": "Payment successful"}, status=status.HTTP_200_OK)


class PaymentCancelAPIView(APIView):
    """
    API view to handle canceled payments.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Handle canceled payments",
        responses={200: "Payment cancellation acknowledged"}
    )
    def get(self, request):
        """
        Handle GET requests for canceled payments.
        """
        transaction_id = request.session.get('transaction_id')
        if not transaction_id:
            return Response({"error": "Transaction ID not found in session"}, status=status.HTTP_400_BAD_REQUEST)

        transaction = get_object_or_404(Transaction, transaction_id=transaction_id)
        transaction.status = 'failed'
        transaction.save()

        return Response({"message": "Payment canceled"}, status=status.HTTP_200_OK)
