import os
import django
import sys
import time

# Add project root to path
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.scraper.models import Product, PriceHistory, StorePrice, Category, Tag
from apps.scraper.stealth_engine import StealthHeaderEngine

User = get_user_model()

def run_verification():
    print("--- Antigravity Phase 1 Verification ---")
    
    # 1. User Model (is_premium)
    user = User.objects.first()
    if user:
        print(f"User: {user.email}, Is Premium: {user.is_premium}")
        if hasattr(user, 'is_premium'):
             print("   [OK] is_premium field exists.")
        else:
             print("   [FAIL] is_premium field missing.")
    
    # 2. Product Tags
    tag, created = Tag.objects.get_or_create(name="Gaming")
    product = Product.objects.first()
    if not product:
         cat, _ = Category.objects.get_or_create(name="TestCat")
         product = Product.objects.create(name="Test Product Phase 1", category=cat, base_price=100)
    
    product.tags.add(tag)
    if product.tags.filter(name="Gaming").exists():
        print("   [OK] Product tags working.")
    else:
        print("   [FAIL] Product tags failed.")

    # 3. Signals & PriceHistory (Automated Analytics)
    print("\n[Testing Signals]")
    # Create StorePrice
    sp, _ = StorePrice.objects.get_or_create(
        product=product, 
        store_name='Amazon',
        defaults={'current_price': 100, 'product_url': 'http://test'}
    )
    
    # Entry 1: 100
    ph1 = PriceHistory.objects.create(store_price=sp, price=100)
    # Give DB a moment for signal to process? Signals are synchronous usually.
    ph1.refresh_from_db()
    print(f"   Entry 1 (100): Change={ph1.change_percentage}, Trend={ph1.trend}, Hash={ph1.integrity_hash[:10]}...")
    
    # Entry 2: 90 (Drop -10%)
    ph2 = PriceHistory.objects.create(store_price=sp, price=90)
    ph2.refresh_from_db()
    print(f"   Entry 2 (90): Change={ph2.change_percentage}%, Trend={ph2.trend}, Hash={ph2.integrity_hash[:10]}...")

    if ph2.change_percentage == -10.00 and ph2.trend == 'DOWN' and ph2.integrity_hash:
        print("   [OK] Automated Signals Working (Math + Hash).")
    else:
        print(f"   [FAIL] Signals failed. Change: {ph2.change_percentage}, Trend: {ph2.trend}")

    # 4. Stealth Engine
    print("\n[Testing Stealth Engine]")
    engine = StealthHeaderEngine()
    headers = engine.get_random_stealth_headers()
    print("   Generated Headers:")
    print(f"   - User-Agent: {headers.get('User-Agent')[:50]}...")
    print(f"   - Sec-Ch-Ua: {headers.get('sec-ch-ua')}")
    
    if headers.get('User-Agent') and headers.get('DNT') == '1':
         print("   [OK] Stealth Headers Generated.")
    else:
         print("   [FAIL] Header generation issues.")

    print("\n--- End Verification ---")

if __name__ == "__main__":
    run_verification()
