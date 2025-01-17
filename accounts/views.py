# account/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .forms import UserRegistrationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .models import CustomUser, UserProfile



def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            # Assign the selected store to the user
            user.store = form.cleaned_data['store']
            user.save()
            messages.success(request, "Your account has been created successfully. Please log in.")
            return redirect('login')  # Redirect to login page after successful registration
    else:
        form = UserRegistrationForm()

    return render(request, 'registration/signup.html', {'form': form})


# Login view
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')  # Get username
        password = request.POST.get('password')  # Get password

        if username and password:
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)

                # Redirect based on role
                role = user.userprofile.role  # Assuming 'role' is in the UserProfile model
                if role == 'admin':
                    return redirect('dashboard:index')  # Redirect to admin dashboard
                elif role == 'cashier':
                    return redirect('billing:sales_view')  # Redirect to sales page
                elif role == 'staff':
                    return redirect('inventory:overview')  # Redirect to inventory management page
                else:
                    return redirect('dashboard:index')  # Default fallback

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



def register_user(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            # Assign user profile and role
            role = form.cleaned_data['role']
            store = request.POST.get('store')  # Assuming store is selected in the form
            UserProfile.objects.create(user=user, store_id=store, role=role)

            return redirect('accounts:login')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})
