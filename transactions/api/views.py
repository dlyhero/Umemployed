from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from transactions.models import Transaction
from users.models import User
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import stripe
from django.conf import settings

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
