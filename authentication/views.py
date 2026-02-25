from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import CustomUserCreationForm
from django_ratelimit.decorators import ratelimit

# Email Verification Imports
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

def register_view(request):
    """
    Handles user registration with email verification.
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Deactivate account until email confirmation
            user.save()

            # Email Verification Logic
            current_site = get_current_site(request)
            mail_subject = 'Activate your account'
            message = render_to_string('registration/acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                mail_subject, message, to=[to_email]
            )
            email.content_subtype = "html" # Main content is text/html
            email.send()

            return render(request, 'registration/activation_sent.html')
        else:
            messages.error(request, "Registration failed. Please check the form for errors.")
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'authentication/register.html', {'form': form})

@ratelimit(key='ip', rate='5/m', block=True)
def login_view(request):
    """
    Handles user login.
    """
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {username}!")
                # Redirect to home/dashboard - typically '/' or a named url 'home'
                return redirect('/') 
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    
    return render(request, 'registration/login.html', {'form': form})

def activate(request, uidb64, token):
    """
    Activates the user account if the token is valid.
    """
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        messages.success(request, "Thank you for your email confirmation. Now you can login your account.")
        return redirect('/')
    else:
        return render(request, 'registration/activation_invalid.html')
