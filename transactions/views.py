from django.shortcuts import render, redirect  
from django.views import View  
from paypal.standard.forms import PayPalPaymentsForm  
from .models import Transaction  
import uuid  
from django.conf import settings  
from paypal.standard.models import ST_PP_COMPLETED  
from paypal.standard.ipn.signals import valid_ipn_received  
from django.contrib.auth.decorators import login_required  
import stripe  
from django.http import JsonResponse  
from django.views.decorators.csrf import csrf_exempt  

# Initialize Stripe API key  
stripe.api_key = settings.STRIPE_SECRET_KEY  

class PayPalPaymentView(View):  
    def get(self, request, *args, **kwargs):  
        transaction_id = str(uuid.uuid4())  
        
        paypal_dict = {  
            'business': settings.PAYPAL_RECEIVER_EMAIL,  # PayPal account email  
            'amount': '5.00',  # Amount to be charged  
            'item_name': 'Test Item',  # Description of the item  
            'invoice': transaction_id,  # Unique transaction/invoice ID  
            'notify_url': request.build_absolute_uri('/transactions/paypal-ipn/'),  # IPN URL  
            'return': request.build_absolute_uri('/transactions/success/'),  # URL to redirect after payment  
            'cancel_return': request.build_absolute_uri('/transactions/cancel/'),  # Cancel URL  
            'currency_code': 'USD',  # Currency code  
        }  

        form = PayPalPaymentsForm(initial=paypal_dict)  
        
        # Only create a transaction if the user is authenticated  
        if request.user.is_authenticated:  
            Transaction.objects.create(  
                user=request.user,  
                transaction_id=transaction_id,  
                amount=paypal_dict['amount'],  
                payment_method='paypal',  # Payment method as PayPal  
                status='pending',  # Status starts as 'Pending'  
            )  
            # Store the transaction ID in the session
            request.session['transaction_id'] = transaction_id

        return render(request, 'transactions/payment.html', {'form': form})  

    def post(self, request, *args, **kwargs):  
        # Handle the payment submission, usually done by PayPal automatically  
        return redirect('payment_success')  # Redirect to success page after form submission  


# IPN (Instant Payment Notification) View for PayPal  
def paypal_ipn(sender, **kwargs):  
    ipn_obj = sender  
    if ipn_obj.payment_status == "Completed":  
        try:  
            # Update the transaction to completed if IPN verifies the payment  
            transaction = Transaction.objects.get(transaction_id=ipn_obj.invoice)  
            transaction.status = 'completed'  
            transaction.save()  
        except Transaction.DoesNotExist:  
            pass  # Handle if transaction doesn't exist  

valid_ipn_received.connect(paypal_ipn)  


# Transaction History View for authenticated users  
@login_required  
def transaction_history(request):  
    transactions = Transaction.objects.filter(user=request.user)  
    return render(request, 'transactions/history.html', {'transactions': transactions})  


from django.http import Http404

def payment_success(request):  
    try:
        # Assuming you have stored the transaction ID in the session
        transaction_id = request.session.get('transaction_id')
        if not transaction_id:
            raise Http404("Transaction ID not found in session")

        transaction = Transaction.objects.get(transaction_id=transaction_id)
        transaction.status = 'completed'
        transaction.save()
        context = {'transaction': transaction}
        return render(request, 'transactions/success.html', context)
    except Transaction.DoesNotExist:
        raise Http404("Transaction does not exist")


def payment_cancel(request):  
    try:
        # Assuming you have stored the transaction ID in the session
        transaction_id = request.session.get('transaction_id')
        if not transaction_id:
            raise Http404("Transaction ID not found in session")

        transaction = Transaction.objects.get(transaction_id=transaction_id)
        transaction.status = 'failed'
        transaction.save()
        context = {'transaction': transaction}
        return render(request, 'transactions/cancel.html', context)
    except Transaction.DoesNotExist:
        raise Http404("Transaction does not exist")

class StripePaymentView(View):  
    def get(self, request, *args, **kwargs):  
        amount = 500  # Amount in cents for Stripe ($5.00)  
        
        # Create Stripe Checkout Session  
        session = stripe.checkout.Session.create(  
            payment_method_types=['card'],  
            line_items=[{  
                'price_data': {  
                    'currency': 'usd',  
                    'product_data': {'name': 'Test Item'},  
                    'unit_amount': amount,  
                },  
                'quantity': 1,  
            }],  
            mode='payment',  
            success_url=request.build_absolute_uri('/transactions/success/'),  
            cancel_url=request.build_absolute_uri('/transactions/cancel/'),  
        )  

        # Use Stripe's session ID as the transaction ID  
        transaction_id = session.id  

        # Create the transaction in the database  
        if request.user.is_authenticated:  
            Transaction.objects.create(  
                user=request.user,  
                transaction_id=transaction_id,  
                amount=amount / 100,  # Convert cents to dollars  
                payment_method='stripe',  
                status='pending',  
            )  
            # Store the transaction ID in the session
            request.session['transaction_id'] = transaction_id

        return JsonResponse({'sessionId': session.id})  


# Webhook handler for Stripe events  
@csrf_exempt  
def stripe_webhook(request):  
    payload = request.body  
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')  
    event = None  

    try:  
        # Verify the webhook signature  
        event = stripe.Webhook.construct_event(  
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET  
        )  
    except ValueError:  
        return JsonResponse({'error': 'Invalid payload'}, status=400)  
    except stripe.error.SignatureVerificationError:  
        return JsonResponse({'error': 'Invalid signature'}, status=400)  

    # Handle successful Stripe checkout event  
    if event['type'] == 'checkout.session.completed':  
        session = event['data']['object']  
        
        try:  
            # Update the transaction using Stripe's session ID  
            transaction = Transaction.objects.get(transaction_id=session['id'])  
            transaction.status = 'completed'  
            transaction.save()  
        except Transaction.DoesNotExist:  
            # Log an error if no transaction matches the session ID  
            print(f"Transaction not found for session ID: {session['id']}")  

    return JsonResponse({'status': 'success'})

from job.models import Rating 
from django.shortcuts import render, get_object_or_404
from users.models import User
def candidate_endorsements(request, candidate_id):
    candidate = get_object_or_404(User, id=candidate_id)
    endorsements = Rating.objects.filter(candidate=candidate)
    context = {
        'candidate': candidate,
        'endorsements': endorsements,
    }
    return render(request, 'job/candidate_endorsements.html', context)