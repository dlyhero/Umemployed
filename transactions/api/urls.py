from django.urls import path
from . import views

urlpatterns = [
    path('paypal-payment/<int:candidate_id>/', views.PayPalPaymentAPIView.as_view(), name='api_paypal_payment'),
    path('stripe-payment/<int:candidate_id>/', views.StripePaymentAPIView.as_view(), name='api_stripe_payment'),
    path('transaction-history/', views.TransactionHistoryAPIView.as_view(), name='api_transaction_history'),
    path('payment-success/', views.PaymentSuccessAPIView.as_view(), name='api_payment_success'),
    path('payment-cancel/', views.PaymentCancelAPIView.as_view(), name='api_payment_cancel'),
]
