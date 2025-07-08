from rest_framework.permissions import BasePermission

from transactions.models import Subscription


class HasActiveSubscription(BasePermission):
    """
    Permission to check if the user has an active subscription with required tier, user_type, or feature.
    Usage:
        - required_tier: restricts to a specific tier (e.g., 'premium')
        - required_user_type: restricts to a user type ('user' or 'recruiter')
        - required_feature: restricts to a feature (e.g., 'resume_enhancer')
    """

    message = "You need to upgrade your plan to access this feature."

    def has_permission(self, request, view):
        required_tier = getattr(view, "required_tier", None)
        required_user_type = getattr(view, "required_user_type", None)
        required_feature = getattr(view, "required_feature", None)

        user = request.user
        if not user or not user.is_authenticated:
            self.message = "Authentication required."
            return False

        subscription = (
            Subscription.objects.filter(user=user, is_active=True).order_by("-started_at").first()
        )
        if not subscription:
            self.message = "No active subscription found. Please upgrade your plan."
            return False

        if required_tier and subscription.tier != required_tier:
            self.message = f"This action requires a {required_tier.capitalize()} plan. Please upgrade your plan."
            return False

        if required_user_type and subscription.user_type != required_user_type:
            self.message = f"This action requires a {required_user_type.capitalize()} subscription."
            return False

        if required_feature and not subscription.has_feature(required_feature):
            self.message = (
                f"This feature requires a plan with '{required_feature}'. Please upgrade your plan."
            )
            return False

        return True
