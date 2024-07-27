# your_project/middleware.py

from django.shortcuts import redirect
from django.urls import reverse

class RedirectBasedOnRoleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Only check after the user has logged in
        if request.user.is_authenticated:
            # Prevent redirect loops by checking the current path
            if request.path == reverse('login') or request.path == reverse('home'):
                # If user is not set as applicant or recruiter, redirect to switch type
                if not request.user.is_applicant and not request.user.is_recruiter:
                    return redirect(reverse('switch_account_type'))  # Adjust URL name if necessary
            # Check if user is on the switch type page to avoid redirecting there
            elif request.path == reverse('switch_account_type') and (request.user.is_applicant or request.user.is_recruiter):
                return redirect(reverse('home'))  # Redirect to home if already applicant or recruiter

        return response
