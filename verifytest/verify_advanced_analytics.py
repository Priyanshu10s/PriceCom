import os
import django
import sys
from decimal import Decimal

# Add project root to path
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.scraper.models import Product, StorePrice, PriceHistory

def run_verification():
    print("--- Advanced Analytics Verification ---")
    
    # 1. Setup Test Data
    # Get or create a product
    product = Product.objects.first()
    if not product:
        print("No products found. Creating one...")
        from apps.scraper.models import Category
        cat, _ = Category.objects.get_or_create(name="TestCat")
        product = Product.objects.create(name="Analytics Test Product", category=cat, base_price=1000)
    
    print(f"Testing on Product: {product.name}")
    
    # Get or create StorePrice
    sp, created = StorePrice.objects.get_or_create(
        product=product, 
        store_name='Amazon',
        defaults={'current_price': 1000, 'product_url': 'http://example.com'}
    )
    
    # Clear old history for this test to be clean
    PriceHistory.objects.filter(store_price=sp).delete()
    
    # 2. Test Step A & B & C & D & E
    print("\n[Step 1] Creating Initial Price Entry (1000.00)")
    ph1 = PriceHistory.objects.create(store_price=sp, price=1000)
    print(f"   Shape: Change={ph1.price_change_percent}%, Trend={ph1.trend}, SigDrop={ph1.is_significant_drop}")
    print(f"   Hash: {ph1.hash_verification[:10]}...")
    
    # Verify Initial State
    if ph1.price_change_percent == 0 and ph1.trend == 'STABLE':
        print("   [OK] Initial entry valid.")
    else:
        print("   [FAIL] Initial entry invalid logic.")

    print("\n[Step 2] Price Drop (900.00) -> -10%")
    ph2 = PriceHistory.objects.create(store_price=sp, price=900)
    print(f"   Shape: Change={ph2.price_change_percent}%, Trend={ph2.trend}, SigDrop={ph2.is_significant_drop}")
    
    if ph2.price_change_percent == -10.00 and ph2.trend == 'DOWN' and ph2.is_significant_drop:
        print("   [OK] Drop logic valid (Significant).")
    else:
        print(f"   [FAIL] Drop logic failed. Expected -10.00, DOWN, True. Got {ph2.price_change_percent}, {ph2.trend}, {ph2.is_significant_drop}")

    print("\n[Step 3] Price Rise (990.00) -> +10%")
    ph3 = PriceHistory.objects.create(store_price=sp, price=990)
    print(f"   Shape: Change={ph3.price_change_percent}%, Trend={ph3.trend}, SigDrop={ph3.is_significant_drop}")
    
    if ph3.price_change_percent == 10.00 and ph3.trend == 'UP' and not ph3.is_significant_drop:
        print("   [OK] Rise logic valid.")
    else:
        print("   [FAIL] Rise logic failed.")

    print("\n[Step 4] Massive Drop (495.00) -> -50%")
    ph4 = PriceHistory.objects.create(store_price=sp, price=495)
    print(f"   Shape: Change={ph4.price_change_percent}%, Trend={ph4.trend}, SigDrop={ph4.is_significant_drop}")

    # 3. Test Custom Manager
    print("\n[Step 5] Testing Custom Manager get_biggest_drops()")
    deals = PriceHistory.objects.get_biggest_drops()
    print(f"   Deals Found: {deals.count()}")
    for d in deals:
        print(f"   - {d.store_price.product.name}: {d.price_change_percent}%")
    
    deals_list = list(deals)
    deal_ids = [d.pk for d in deals_list]
    
    # Logic note: get_biggest_drops only returns the LATEST entry per product if it is a drop.
    # In our test sequence:
    # 1. 1000 (stable)
    # 2. 900 (-10% drop)
    # 3. 990 (+10% rise)
    # 4. 495 (-50% drop) -> Latest
    # So we should ONLY see ph4 (-50%) and NOT ph2 (-10%) because ph2 is not the latest for that product.
    
    if ph4.pk in deal_ids and ph2.pk not in deal_ids:
        print("   [OK] Custom Manager filtered for latest drops only.")
    else:
        print(f"   [FAIL] Custom Manager logic incorrect. IDs found: {deal_ids}. Expected {ph4.pk} only.")

    print("\n--- End Verification ---")

if __name__ == "__main__":
    run_verification()
