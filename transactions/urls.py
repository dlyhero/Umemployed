# transactions/urls.py

from django.urls import path
from django.views.generic import TemplateView
from .views import PayPalPaymentView, paypal_ipn,transaction_history

urlpatterns = [
    path('pay/', PayPalPaymentView.as_view(), name='paypal-payment'),
    path('paypal-ipn/', paypal_ipn, name='paypal-ipn'),
    path('success/', TemplateView.as_view(template_name='transactions/success.html'), name='payment_success'),
    path('cancel/', TemplateView.as_view(template_name='transactions/cancel.html'), name='payment_cancel'),
    path('paypal-return/', paypal_ipn, name='paypal_ipn'),
    path('history/', transaction_history, name='transaction_history'),

]