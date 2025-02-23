# account/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .forms import UserRegistrationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .models import CustomUser, UserProfile
from .models import UserProfile  
from .utils import generate_new_cart_id



from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import UserRegistrationForm



from django.contrib.auth import get_user_model
from .models import UserProfile

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()  # Save the user first
            UserProfile.objects.create(user=user)  # Create a UserProfile for the user
            messages.success(request, 'Registration successful! Please log in.')
            return redirect('accounts:login')
        else:
            messages.error(request, 'Registration failed, please correct the errors below.')
    else:
        form = UserRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .models import UserProfile

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')  # Get username
        password = request.POST.get('password')  # Get password

        if username and password:
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)

                # Check if cart_id exists in session, create a new one if not
                if 'cart_id' not in request.session:
                    request.session['cart_id'] = generate_new_cart_id()  # Create new 10-digit cart_id for this session
                    print(f"New cart_id created: {request.session['cart_id']}")  # Debugging line
                
                try:
                    # Retrieve the user's profile and role
                    user_profile = UserProfile.objects.get(user=user)
                    role = user_profile.role  # Assuming 'role' is in the UserProfile model

                    # Redirect based on role
                    if role:
                        return redirect('dashboard:index')  # Redirect to the index page in the dashboard
                    else:
                        return redirect('accounts:login')
                except UserProfile.DoesNotExist:
                    # Handle case where the user profile does not exist
                    error_message = "User profile does not exist."
                    return render(request, 'accounts/login.html', {'error': error_message})

            else:
                error_message = "Invalid login credentials"
                return render(request, 'accounts/login.html', {'error': error_message})
        else:
            error_message = "Both username and password are required"
            return render(request, 'accounts/login.html', {'error': error_message})

    return render(request, 'accounts/login.html')


# Logout view
def user_logout(request):
    logout(request)
    request.session.flush()
    return redirect('accounts:login')  # Redirect to login page after logout

from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm

def user_signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your account has been created successfully. Please log in.")
            return redirect('accounts:login')  # Redirect to login page after successful signup
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})


from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .models import UserProfile, CustomUser
from .models import CustomUser, UserProfile

def register_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')

        if password == password_confirm:
            # Create the user
            user = CustomUser.objects.create_user(username=username, email=email, password=password)
            user.save()

            # Create the UserProfile
            UserProfile.objects.create(user=user)

            return redirect('accounts:login')
        else:
            error_message = "Passwords do not match"
            return render(request, 'accounts/register.html', {'error': error_message})

    return render(request, 'accounts/register.html')

# views.py
from django.shortcuts import render

def auth_view(request):
    # Custom view logic
    return render(request, 'password_reset_form.html')
