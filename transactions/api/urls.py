from django.urls import path

from . import views
from .views import StripeWebhookAPIView

urlpatterns = [
    path(
        "paypal-payment/<int:candidate_id>/",
        views.PayPalPaymentAPIView.as_view(),
        name="api_paypal_payment",
    ),
    path(
        "stripe-payment/<int:candidate_id>/",
        views.StripePaymentAPIView.as_view(),
        name="api_stripe_payment",
    ),
    path(
        "transaction-history/",
        views.TransactionHistoryAPIView.as_view(),
        name="api_transaction_history",
    ),
    path("payment-success/", views.PaymentSuccessAPIView.as_view(), name="api_payment_success"),
    path("payment-cancel/", views.PaymentCancelAPIView.as_view(), name="api_payment_cancel"),
    path(
        "stripe-subscribe/",
        views.CreateStripeSubscriptionAPIView.as_view(),
        name="api_stripe_subscribe",
    ),
    path(
        "stripe-cancel/", views.CancelStripeSubscriptionAPIView.as_view(), name="api_stripe_cancel"
    ),
    path("stripe/webhook/", StripeWebhookAPIView.as_view(), name="stripe-webhook"),
    path(
        "subscription-status/<int:user_id>/",
        views.SubscriptionStatusAPIView.as_view(),
        name="api_subscription_status",
    ),
    path(
        "subscription-debug/",
        views.SubscriptionDebugAPIView.as_view(),
        name="api_subscription_debug",
    ),
    path(
        "endorsement-subscribe/",
        views.CreateEndorsementSubscriptionAPIView.as_view(),
        name="api_endorsement_subscribe",
    ),
    path(
        "endorsement-subscription-status/",
        views.EndorsementSubscriptionStatusAPIView.as_view(),
        name="api_endorsement_subscription_status",
    ),
]
