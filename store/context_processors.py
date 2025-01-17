# store/context_processors.py

from .models import Store

def store(request):
    # Check if the user is authenticated and has a store assigned
    if request.user.is_authenticated and hasattr(request.user, 'staff') and hasattr(request.user.staff, 'store'):
        store = request.user.staff.store
        return {'store': store}
    return {}
