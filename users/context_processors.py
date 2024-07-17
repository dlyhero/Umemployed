# your_app/context_processors.py

from company.models import Company  # Import your Company model

def add_company_to_context(request):
    if request.user.is_authenticated and request.user.has_company:
        try:
            company = Company.objects.get(user=request.user)
            return {
                'user_company': company
            }
        except Company.DoesNotExist:
            return {
                'user_company': None
            }
    return {}
