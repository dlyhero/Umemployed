# In your_app/pipeline.py

from social_core.exceptions import AuthException
from social_core.pipeline.partial import partial


@partial
def associate_by_email(strategy, details, user=None, *args, **kwargs):
    if user:
        return {"is_new": False}

    email = details.get("email")
    if not email:
        raise AuthException(strategy.backend, "No email provided")

    try:
        existing_user = strategy.storage.user.get_user(email=email)
        if existing_user:
            return {"is_new": False, "user": existing_user}
    except strategy.storage.user.User.DoesNotExist:
        return {"is_new": True}

    return {"is_new": True}
