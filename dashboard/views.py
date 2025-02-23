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

