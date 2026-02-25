import os
import django
import sys
import datetime
from django.utils import timezone

# Add project root to path
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.scraper.timezone_utils import get_utc_now, is_price_stale, sync_api_timestamp
from apps.scraper.models import Product, Category

def run_verification():
    print("--- Timezone Hardening Verification ---")
    
    # 1. Check Global Settings
    print(f"Time Zone: {django.conf.settings.TIME_ZONE}")
    print(f"Use TZ: {django.conf.settings.USE_TZ}")
    if django.conf.settings.TIME_ZONE == 'UTC' and django.conf.settings.USE_TZ:
        print("   [OK] Global Settings Correct")
    else:
        print("   [FAIL] Global Settings Incorrect")

    # 2. Test get_utc_now
    now = get_utc_now()
    print(f"Current UTC Now: {now}")
    if timezone.is_aware(now):
        print("   [OK] get_utc_now returns Aware Datetime")
    else:
         print("   [FAIL] get_utc_now returns Naive Datetime")

    # 3. Test is_price_stale
    # Case A: Fresh
    fresh_time = now - datetime.timedelta(hours=1)
    if not is_price_stale(fresh_time, 6):
        print("   [OK] Fresh item identified correctly")
    else:
        print("   [FAIL] Fresh item marked as stale")
        
    # Case B: Stale
    stale_time = now - datetime.timedelta(hours=7)
    if is_price_stale(stale_time, 6):
        print("   [OK] Stale item identified correctly")
    else:
        print("   [FAIL] Stale item marked as fresh")

    # 4. Test Local Conversion (Product Model)
    cat, _ = Category.objects.get_or_create(name='TimeTest')
    p = Product(name="Time Test Product", category=cat, base_price=10)
    p.save() # updated_at set to UTC now
    
    local_time = p.get_local_updated_time('Asia/Kolkata')
    print(f"UTC Time: {p.updated_at}")
    print(f"IST Time: {local_time}")
    
    # Check offset (IST is UTC+5:30)
    # Simple check: IST should be > UTC value numerically if printed simply, but they represent same point.
    # Let's check the tzinfo
    if str(local_time.tzinfo) == 'Asia/Kolkata':
        print("   [OK] Local Conversion Successful")
    else:
        print(f"   [FAIL] Local Conversion returned {local_time.tzinfo}")

    p.delete()
    cat.delete()
    print("\n--- End Verification ---")

if __name__ == "__main__":
    run_verification()
