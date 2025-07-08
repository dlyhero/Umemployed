# job/decorators.py
from functools import wraps

from django.http import HttpResponseForbidden

from .models import Company


def company_belongs_to_user(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        company_id = kwargs.get("company_id")
        try:
            company = Company.objects.get(id=company_id, user=request.user)
        except Company.DoesNotExist:
            return HttpResponseForbidden("You are not authorized to access this company.")
        return view_func(request, *args, **kwargs)

    return _wrapped_view
