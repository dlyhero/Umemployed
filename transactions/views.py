from django.shortcuts import render, redirect
from django.views import View
from paypal.standard.forms import PayPalPaymentsForm
from .models import Transaction
import uuid
from django.conf import settings
from paypal.standard.models import ST_PP_COMPLETED
from paypal.standard.ipn.signals import valid_ipn_received
from django.contrib.auth.decorators import login_required


class PayPalPaymentView(View):
    def get(self, request, *args, **kwargs):
        transaction_id = str(uuid.uuid4())
        paypal_dict = {
            'business': settings.PAYPAL_RECEIVER_EMAIL,  # Replace with your PayPal sandbox email
            'amount': '5.00',  # Amount to be charged
            'item_name': 'Test UmEmployed',
            'invoice': transaction_id,  # Unique invoice ID
            'notify_url': request.build_absolute_uri('/paypal-ipn/'),  # IPN URL
            'return': request.build_absolute_uri('/transactions/success/'),  # Return URL after payment
            'cancel_return': request.build_absolute_uri('/transactions/cancel/'),  # Cancellation URL
            'currency_code': 'USD',  # Currency code
        }

        form = PayPalPaymentsForm(initial=paypal_dict)
        if request.user.is_authenticated:
            Transaction.objects.create(
                user=request.user,
                transaction_id=transaction_id,
                amount=paypal_dict['amount'],
                status='Pending'
            )
        return render(request, 'transactions/payment.html', {'form': form})

    def post(self, request, *args, **kwargs):
        # Handle PayPal payment form submission (usually handled by PayPal after GET)
        return redirect('payment_success')  # Redirect to success page after form submission


# IPN view to handle the PayPal notifications (Background processing)
def paypal_ipn(sender, **kwargs):
    ipn_obj = sender
    if ipn_obj.payment_status == ST_PP_COMPLETED:
        try:
            transaction = Transaction.objects.get(transaction_id=ipn_obj.invoice)
            transaction.status = 'Completed'
            transaction.save()
        except Transaction.DoesNotExist:
            pass

valid_ipn_received.connect(paypal_ipn)

# Transaction History for authenticated users
@login_required
def transaction_history(request):
    transactions = Transaction.objects.filter(user=request.user)
    return render(request, 'transactions/history.html', {'transactions': transactions})

def payment_success(request):
    return render(request, 'transactions/success.html')
def payment_cancel(request):
    return render(request, 'transactions/cancel.html')
