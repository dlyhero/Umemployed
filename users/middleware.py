# middleware.py
from django.shortcuts import redirect
from django.urls import reverse

class EmailVerificationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and not request.user.emailaddress_set.filter(verified=True).exists():
            if request.path not in [reverse('verify_email'), reverse('account_logout')]:
                return redirect('account_email_verification_sent')
        response = self.get_response(request)
        return response