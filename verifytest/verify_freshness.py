import os
import django
import sys
from datetime import timedelta
from django.utils import timezone

# Add project root to path
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.scraper.models import Product, Category

def run_verification():
    print("--- Freshness Logic Verification ---")
    
    # Setup Data
    cat, _ = Category.objects.get_or_create(name='FreshTest')
    
    # 1. Live Product (< 1 hr)
    live_prod = Product(name="Live Item", category=cat, base_price=100)
    # Mock updated_at (can't set directly if auto_now=True usually, but for unit test object instantiation we can try, 
    # or save then update via update() to bypass auto_now if needed, but let's test the method logic mainly)
    # Actually auto_now=True overrides on save.
    # Pattern: Save -> Manually update timestamp via queryset.update() to simulate time passing.
    live_prod.save() 
    # It just saved, so it's fresh (0 min old)
    stat = live_prod.get_freshness_status()
    print(f"   [Live] 0m old -> {stat}")
    if stat == 'status-live': print("   [OK] Live Detected")
    else: print("   [FAIL] Live logic wrong")

    # 2. Delayed Product (2 hours old)
    delayed_prod = Product.objects.create(name="Delayed Item", category=cat, base_price=100)
    Product.objects.filter(pk=delayed_prod.pk).update(updated_at=timezone.now() - timedelta(hours=2))
    # Reload from DB to get updated field
    delayed_prod.refresh_from_db()
    
    stat = delayed_prod.get_freshness_status()
    print(f"   [Delayed] 2h old -> {stat}")
    if stat == 'status-delayed': print("   [OK] Delayed Detected")
    else: print("   [FAIL] Delayed logic wrong")

    # 3. Stale Product (25 hours old)
    stale_prod = Product.objects.create(name="Stale Item", category=cat, base_price=100)
    Product.objects.filter(pk=stale_prod.pk).update(updated_at=timezone.now() - timedelta(hours=25))
    stale_prod.refresh_from_db()
    
    stat = stale_prod.get_freshness_status()
    print(f"   [Stale] 25h old -> {stat}")
    if stat == 'status-stale': print("   [OK] Stale Detected")
    else: print("   [FAIL] Stale logic wrong")

    # Clean up
    live_prod.delete()
    delayed_prod.delete()
    stale_prod.delete()
    cat.delete()
    
    print("\n--- End Verification ---")

if __name__ == "__main__":
    run_verification()
