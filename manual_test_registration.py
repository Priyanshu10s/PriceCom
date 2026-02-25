import os
import django
import uuid
from django.test import Client
from django.urls import reverse

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.accounts.forms import CustomUserCreationForm

User = get_user_model()

def test_registration():
    client = Client()
    
    # Generate unique user data
    unique_id = str(uuid.uuid4())[:8]
    username = f"testuser_{unique_id}"
    email = f"test_{unique_id}@example.com"
    password = "TestPassword123!"
    
    print(f"Attempting to register user: {username} / {email}")
    
    try:
        url = reverse('register')
    except Exception:
        try:
            url = reverse('accounts:register')
        except Exception as e:
            print(f"Could not reverse URL: {e}")
            return

    print(f"Posting to {url}...")
    
    # Based on form inspection: ['username', 'email', 'password1', 'password2']
    response = client.post(url, {
        'username': username,
        'email': email,
        'password1': password,
        'password2': password,
    })
    
    print(f"Response Status Code: {response.status_code}")
    
    if response.status_code == 302:
        print("SUCCESS: Registration redirected (likely to login page).")
        print(f"Redirect URL: {response.url}")
        
        # Verify user exists
        if User.objects.filter(username=username).exists():
            print(f"SUCCESS: User {username} created in database.")
        else:
            print(f"FAILURE: User {username} NOT found in database.")
            
    else:
        print("FAILURE: Registration did not redirect.")
        print("Form Errors (if any):")
        # Access the context to see form errors if available
        if 'form' in response.context:
            print(response.context['form'].errors)
        else:
            print(response.content.decode('utf-8')[:500]) # Print first 500 chars of content

if __name__ == "__main__":
    test_registration()
