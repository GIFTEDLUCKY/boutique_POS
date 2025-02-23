from functools import wraps
from django.shortcuts import redirect

def role_required(allowed_roles, store_required=False):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Check the user's role
            if request.user.is_authenticated:
                user_role = request.user.userprofile.role
                user_store = request.user.userprofile.store

                # Check if the user has the allowed role
                if user_role not in allowed_roles:
                    return redirect('accounts:login')  # Redirect to login or a 'permission denied' page

                # Check if the store access is required (for cashiers)
                if store_required and user_store != kwargs.get('store'):
                    return redirect('accounts:login')  # Redirect to login or a 'permission denied' page

                return view_func(request, *args, **kwargs)
            return redirect('accounts:login')  # Redirect to login if user is not authenticated
        return _wrapped_view
    return decorator
