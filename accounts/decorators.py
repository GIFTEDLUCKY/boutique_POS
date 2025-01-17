# accounts/decorators.py
from django.shortcuts import redirect
from functools import wraps

# Custom decorator to check if the user has the required role
def role_required(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Check the user's role
            if request.user.is_authenticated and request.user.userprofile.role not in allowed_roles:
                return redirect('accounts:login')  # Redirect to login or a 'permission denied' page
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
