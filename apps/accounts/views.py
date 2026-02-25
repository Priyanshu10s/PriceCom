from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import CustomUserCreationForm
from django_ratelimit.decorators import ratelimit
from django.conf import settings

def register_view(request):
    """
    Handles user registration.
    Prevents logged-in users from accessing the registration page.
    """
    if request.user.is_authenticated:
        return redirect('dashboard:index')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Option 1: Log them in immediately
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, "Registration Successful! Welcome to Dashboard.")
            return redirect('dashboard:index')
            
            # Option 2: Redirect to login (if you prefer strict flow)
            # messages.success(request, "Account created successfully! Please log in.")
            # return redirect('login')
        else:
            messages.error(request, "Registration failed. Please correct the errors below.")
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

@ratelimit(key='ip', rate='5/m', block=True)
def login_view(request):
    """
    Handles user login with rate limiting (5 attempts per minute).
    Prevents logged-in users from accessing the login page.
    """
    if request.user.is_authenticated:
        return redirect('dashboard:index')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {username}!")
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('dashboard:index')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    """
    Handles user logout.
    """
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('login')
