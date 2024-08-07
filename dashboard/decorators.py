from functools import wraps
from django.shortcuts import redirect
from django.urls import reverse

def resume_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse('login'))
        if not request.user.has_resume:
            return redirect(reverse('upload'))
        return view_func(request, *args, **kwargs)
    return _wrapped_view
