# middleware.py
from django.shortcuts import redirect
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch

class EmailVerificationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            excluded_paths = [
                reverse('verify_email'),
                reverse('account_logout'),
                reverse('account_email_verification_sent'),
                reverse('logout'),
                reverse('resend_verification_email'),
            ]
            # Add the base path for the email confirmation URL
            confirm_email_base_path = reverse('account_confirm_email', kwargs={'key': 'dummy-key'}).rsplit('/', 2)[0]
            excluded_paths.append(confirm_email_base_path)
        except NoReverseMatch:
            excluded_paths = []

        if request.user.is_authenticated and not request.user.emailaddress_set.filter(verified=True).exists():
            if not any(request.path.startswith(path) for path in excluded_paths):
                return redirect('account_email_verification_sent')
        
        response = self.get_response(request)
        return response