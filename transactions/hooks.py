from django.dispatch import receiver
from paypal.standard.models import ST_PP_COMPLETED
from paypal.standard.ipn.signals import valid_ipn_received
from .models import Transaction
import logging

logger = logging.getLogger(__name__)

@receiver(valid_ipn_received)
def paypal_payment_received(sender, **kwargs):
    ipn_obj = sender

    # Check if the payment was completed
    if ipn_obj.payment_status == ST_PP_COMPLETED:
        logger.info(f"Payment received from {ipn_obj.payer_email} for {ipn_obj.mc_gross} {ipn_obj.mc_currency}")

        try:
            # Find the transaction based on the PayPal invoice ID (transaction_id)
            transaction = Transaction.objects.get(transaction_id=ipn_obj.invoice)
            transaction.status = 'Completed'
            transaction.save()
            logger.info(f"Transaction {ipn_obj.invoice} status updated to Completed")
        except Transaction.DoesNotExist:
            logger.error(f"Transaction with invoice {ipn_obj.invoice} not found")

    else:
        logger.info(f"Payment status was not completed: {ipn_obj.payment_status}")
