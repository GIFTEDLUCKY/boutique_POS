from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist

from django.shortcuts import render, redirect


from django.contrib.auth.decorators import login_required


@login_required
def index(request):
    if request.user.is_authenticated:
        # Access userprofile only for authenticated users
        user_profile = request.user.userprofile
        # Do something with user_profile
        return render(request, 'dashboard/index.html', {'user_profile': user_profile})
    else:
        # Redirect to login or display a message
        return redirect('accounts:login')  # Replace 'login' with the name of your login URL

# views.py
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def continue_project(request):
    if request.method == 'POST':
        # ✅ Must match middleware key exactly
        request.session['skip_license_warning'] = True

        # If user is authenticated, send to homepage/dashboard
        if request.user.is_authenticated:
            return redirect('/')  # Or your dashboard page

        # Otherwise, go to login page
        return redirect('accounts:login')
    
    # If someone tries GET instead of POST
    return redirect('/')


# dashboard/views.py
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

@login_required
def keepalive(request):
    """
    Simple endpoint for AJAX keep-alive pings.
    Called periodically by JavaScript to prevent session timeout.
    """
    return JsonResponse({"status": "alive"})
