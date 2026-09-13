"""Role based access control helpers."""
from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def role_required(*roles):
    """Allow the view only for the given roles (superusers always pass)."""

    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped(request, *args, **kwargs):
            user = request.user
            if user.is_superuser or user.role in roles:
                return view_func(request, *args, **kwargs)
            raise PermissionDenied("You do not have permission to open this page.")

        return _wrapped

    return decorator


#: Convenience shortcuts used all over the project
admin_required = role_required("ADMIN")
staff_required = role_required("ADMIN", "DOCTOR", "RECEPTIONIST")
front_desk_required = role_required("ADMIN", "RECEPTIONIST")
clinical_required = role_required("ADMIN", "DOCTOR")
