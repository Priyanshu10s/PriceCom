
import os
import django
import logging

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings
from django.test import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.models import AnonymousUser
from apps.dashboard.models import Cart, CartItem, RedirectionLog
from apps.scraper.models import Product, Category, StorePrice
from apps.dashboard.utils import get_or_create_cart, sync_cart_session_to_db
from apps.dashboard.views import redirect_to_merchant
from django.contrib.auth import get_user_model

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
User = get_user_model()

def verify_cart_and_redirect():
    print("--- Antigravity Cart & Redirection Verification ---")
    
    # 1. Setup Data
    user, _ = User.objects.get_or_create(email='cart_tester@example.com', defaults={'username': 'cart_tester'})
    category, _ = Category.objects.get_or_create(name='TestCat')
    product, _ = Product.objects.get_or_create(name='TestProduct', category=category)
    
    # Ensure StorePrice exists for redirection
    StorePrice.objects.get_or_create(
        product=product, 
        store_name='Amazon', 
        defaults={
            'current_price': 100.00, 
            'product_url': 'http://amazon.com/test'
        }
    )

    # 2. Test Guest Cart Creation
    print("\n[1] Testing Guest Cart...")
    factory = RequestFactory()
    request = factory.get('/')
    
    # Add Session Middleware support manually
    middleware = SessionMiddleware(lambda x: None)
    middleware.process_request(request)
    request.session.save()
    
    request.user = AnonymousUser()
    
    cart = get_or_create_cart(request)
    print(f"[PASS] Created Guest Cart: ID {cart.id} (User: {cart.user})")
    
    # Add Item to Guest Cart
    CartItem.objects.create(
        cart=cart, 
        product=product, 
        price_at_addition=99.00, 
        best_store_at_addition='Amazon',
        affiliate_url='http://amazon.com/test'
    )
    print(f"[PASS] Added Item to Guest Cart: {cart.items.first()}")
    
    # 3. Test Sync-on-Login
    print("\n[2] Testing Sync-on-Login...")
    # Simulate Login by manually calling the sync util (Signal calls this)
    sync_cart_session_to_db(request, user)
    
    # Verify User Cart matches Guest Cart items
    user_cart = Cart.objects.get(user=user)
    print(f"[PASS] User Cart ID {user_cart.id} Items: {user_cart.items.count()}")
    
    if user_cart.items.filter(product=product).exists():
        print(" -> SYNC LOGIC: FUNCTIONAL")
    else:
        print(" -> SYNC LOGIC: FAILED")
        
    # 4. Test Redirection Gateway
    print("\n[3] Testing Redirection Gateway...")
    redirect_request = factory.get(f'/dashboard/redirect/?product_id={product.uuid}&store=Amazon&url=http://amazon.com/test')
    redirect_request.user = user
    redirect_request.session = request.session
    
    # Execute View
    response = redirect_to_merchant(redirect_request)
    
    # Verify Redirect
    if response.status_code == 302 and response.url == 'http://amazon.com/test':
        print(f"[PASS] Redirection Status: {response.status_code} -> {response.url}")
    else:
         print(f"[FAIL] Redirection Status: {response.status_code}")

    # Verify Log
    log_exists = RedirectionLog.objects.filter(product=product, user=user).exists()
    if log_exists:
        print(" -> INTENT LOGGING: FUNCTIONAL")
    else:
        print(" -> INTENT LOGGING: FAILED")

if __name__ == "__main__":
    verify_cart_and_redirect()
