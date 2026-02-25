
import os
import django
import logging
from unittest.mock import patch

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.cache import cache
from apps.scraper.tasks import send_price_alert_email
from apps.scraper.models import Product, Category
from django.contrib.auth import get_user_model

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
User = get_user_model()

def verify_frequency_capping():
    print("--- Smart Watcher Verification: Frequency Capping ---")
    
    # 1. Setup Data
    user, _ = User.objects.get_or_create(email='watcher_test@example.com', defaults={'username': 'watcher_test'})
    category, _ = Category.objects.get_or_create(name='WatcherCat')
    product, _ = Product.objects.get_or_create(name='WatcherProduct', category=category)
    
    # 2. Clear Cache (Ensure clean slate)
    cache_key = f"alert_cool_down_{user.id}_{product.id}"
    cache.delete(cache_key)
    
    # 3. Test First Alert (Should Send)
    print("\n[1] Sending First Alert...")
    with patch('apps.scraper.tasks.send_monitored_email') as mock_email:
        mock_email.return_value = True
        
        result = send_price_alert_email(
            user_id=user.id,
            subject="Test Alert",
            message="Price Drop!",
            product_id=product.id,
            current_price="100.00"
        )
        print(f"Result 1: {result}")
        
        if "Email Sent" in result:
             print("[PASS] First Alert Sent.")
        else:
             print("[FAIL] First Alert Failed.")

    # 4. Test Second Alert (Should Suppress)
    print("\n[2] Sending Duplicate Alert (Immediate)...")
    with patch('apps.scraper.tasks.send_monitored_email') as mock_email:
        mock_email.return_value = True
        
        result_2 = send_price_alert_email(
            user_id=user.id,
            subject="Test Alert 2",
            message="Price Drop!",
            product_id=product.id,
            current_price="90.00"
        )
        print(f"Result 2: {result_2}")
        
        if "Skipped: Cool-down active" in result_2:
             print("[PASS] Duplicate Alert Suppressed (Cool-down functional).")
        else:
             print("[FAIL] Duplicate Alert check failed.")

if __name__ == "__main__":
    verify_frequency_capping()
