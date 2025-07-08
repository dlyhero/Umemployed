# transactions/urls.py

from django.urls import path
from django.views.generic import TemplateView

from .views import (
    PayPalPaymentView,
    StripePaymentView,
    candidate_endorsements,
    payment_cancel,
    payment_success,
    paypal_ipn,
    stripe_webhook,
    transaction_history,
)

urlpatterns = [
    path("pay/", PayPalPaymentView.as_view(), name="paypal-payment"),
    path("paypal-ipn/", paypal_ipn, name="paypal-ipn"),
    # path('success/', TemplateView.as_view(template_name='transactions/success.html'), name='payment_success'),
    # path('cancel/', TemplateView.as_view(template_name='transactions/cancel.html'), name='payment_cancel'),
    path("paypal-return/", paypal_ipn, name="paypal_ipn"),
    # path('history/', transaction_history, name='transaction_history'),
    # stripe
    path("stripe-payment/", StripePaymentView.as_view(), name="stripe_payment"),
    path("stripe-webhook/", stripe_webhook, name="stripe_webhook"),
    path("success/", payment_success, name="payment_success"),
    path("cancel/", payment_cancel, name="payment_cancel"),
    path(
        "candidate/<int:candidate_id>/endorsements/",
        candidate_endorsements,
        name="candidate_endorsements",
    ),
    path("history/", transaction_history, name="transaction_history"),
    # path('history/<int:candidate_id>/', transaction_history, name='candidate_transaction_history'),
]
