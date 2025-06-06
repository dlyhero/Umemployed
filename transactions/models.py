from django.db import models
from users.models import User

from django.db import models
from django.conf import settings
from django.utils import timezone

class Transaction(models.Model):
    PAYMENT_METHODS = [
        ('paypal', 'PayPal'),
        ('stripe', 'Stripe'),
        # Add other payment providers here as needed
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    candidate = models.ForeignKey(User, on_delete=models.CASCADE, related_name='candidate_transactions', null=True, blank=True)
    transaction_id = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    description = models.TextField(null=True, blank=True)  # Optional description for more info
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.payment_method.capitalize()} Transaction {self.transaction_id} - {self.status}'

class Subscription(models.Model):
    TIER_CHOICES = [
        ('basic', 'Basic'),
        ('standard', 'Standard'),
        ('premium', 'Premium'),
        ('custom', 'Custom'),  # For recruiters only
        ('endorsement', 'Endorsement'),  # For endorsement subscription
    ]
    USER_TYPE_CHOICES = [
        ('user', 'User'),
        ('recruiter', 'Recruiter'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    tier = models.CharField(max_length=20, choices=TIER_CHOICES)  # Increased from 10 to 20
    is_active = models.BooleanField(default=True)
    stripe_subscription_id = models.CharField(max_length=100, null=True, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    # For custom pricing inquiries
    custom_inquiry = models.TextField(null=True, blank=True)

    # Define features available for each tier and user_type
    FEATURES_BY_TIER = {
        ('user', 'basic'): [],
        ('user', 'standard'): [],
        ('user', 'premium'): ['resume_enhancer', 'top_applicant'],
        ('recruiter', 'basic'): [],
        ('recruiter', 'standard'): [],
        ('recruiter', 'premium'): ['ai_job_description', 'free_endorsement'],
        ('recruiter', 'custom'): ['custom_features'],
    }

    def __str__(self):
        return f"{self.user} - {self.user_type} - {self.tier} ({'Active' if self.is_active else 'Inactive'})"

    def get_daily_limit(self):
        # Returns the daily limit based on tier and user_type
        if self.tier == 'basic':
            return 5 if self.user_type == 'user' else 1
        if self.tier == 'standard':
            return 20 if self.user_type == 'user' else 5
        if self.tier == 'premium':
            return None if self.user_type == 'user' else 20  # None = unlimited for users
        if self.tier == 'custom':
            return None  # Custom logic elsewhere
        return None

    def can_perform_action(self, usage_type):
        # Safeguard: Only allow if subscription is active
        if not self.is_active:
            return False
        today = timezone.now().date()
        usage, created = DailyUsage.objects.get_or_create(
            user=self.user, date=today, usage_type=usage_type
        )
        # If the record is not for today, reset the count
        if not created and usage.date != today:
            usage.count = 0
            usage.date = today
            usage.save()
        limit = self.get_daily_limit()
        if limit is None:
            return True  # Unlimited
        return usage.count < limit

    def increment_usage(self, usage_type):
        # Safeguard: Only increment if subscription is active
        if not self.is_active:
            return
        from django.utils import timezone
        today = timezone.now().date()
        usage, created = DailyUsage.objects.get_or_create(
            user=self.user, date=today, usage_type=usage_type
        )
        # If the record is not for today, reset the count
        if not created and usage.date != today:
            usage.count = 0
            usage.date = today
        usage.count += 1
        usage.save()

    def has_feature(self, feature_name):
        tier_order = ['basic', 'standard', 'premium', 'custom']
        user_type = self.user_type
        current_tier_index = tier_order.index(self.tier)
        for tier in reversed(tier_order[:current_tier_index + 1]):
            if feature_name in self.FEATURES_BY_TIER.get((user_type, tier), []):
                return True
        return False

class DailyUsage(models.Model):
    USAGE_TYPE_CHOICES = [
        ('application', 'Application'),
        ('posting', 'Posting'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_usages')
    date = models.DateField(auto_now_add=True)
    usage_type = models.CharField(max_length=20, choices=USAGE_TYPE_CHOICES)
    count = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('user', 'date', 'usage_type')

    def __str__(self):
        return f"{self.user} - {self.usage_type} on {self.date}: {self.count}"
