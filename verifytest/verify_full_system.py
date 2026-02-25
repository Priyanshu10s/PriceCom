import os
import django
import sys
import uuid
from decimal import Decimal
from django.utils import timezone
from django.test import RequestFactory

# Add project root to path
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.accounts.models import User
from apps.scraper.models import Product, Category, StorePrice, PriceHistory, Watchlist, PriceAlert
from apps.scraper.scraper_engine import ScraperFactory
from apps.dashboard.views import dashboard_home
from apps.scraper.timezone_utils import get_utc_now

def run_full_system_check():
    print("--- FINAL SYSTEM VERIFICATION ---")
    
    # 1. Database & Models
    print("\n1. [Database Integrity]")
    try:
        user_count = User.objects.count()
        prod_count = Product.objects.count()
        print(f"   - Users: {user_count}")
        print(f"   - Products: {prod_count}")
        print("   [OK] Database Connection")
    except Exception as e:
        print(f"   [FAIL] Database Error: {e}")
        return

    # 2. Scraper Architecture
    print("\n2. [Scraper Architecture]")
    try:
        adapter = ScraperFactory.get_scraper('Amazon')
        if adapter:
            print("   [OK] Amazon Adapter Loaded")
        else:
            print("   [FAIL] Adapter Factory Failed")
    except Exception as e:
        print(f"   [FAIL] Scraper Error: {e}")

    # 3. Analytics Engine (Simulation)
    print("\n3. [Analytics Engine]")
    try:
        # Create Test Data
        test_user, _ = User.objects.get_or_create(email="test@analytics.com", defaults={'username': 'testeval'})
        cat, _ = Category.objects.get_or_create(name="AnalyticsTest")
        p = Product.objects.create(name="Analytics Item", category=cat, base_price=1000, current_lowest_price=800)
        Watchlist.objects.create(user=test_user, product=p, target_price=900)
        
        # Simulate Request
        factory = RequestFactory()
        request = factory.get('/dashboard/')
        request.user = test_user
        
        response = dashboard_home(request)
        if response.status_code == 200:
             print("   [OK] Dashboard View Returns 200")
             # We can't easily check context without rendering, but 200 implies no crash
        else:
             print(f"   [FAIL] Dashboard returned {response.status_code}")
             
        # Cleanup
        p.delete()
        cat.delete()
        test_user.delete()
    except Exception as e:
        print(f"   [FAIL] Analytics Error: {e}")

    # 4. Security Layer (UUIDs)
    print("\n4. [Security Layer]")
    try:
        p_sec = Product.objects.create(name="SecureItem")
        if isinstance(p_sec.uuid, uuid.UUID):
            print(f"   [OK] UUID Generated: {p_sec.uuid}")
        else:
            print(f"   [FAIL] UUID Missing or Invalid: {p_sec.uuid}")
        p_sec.delete()
    except Exception as e:
        print(f"   [FAIL] Security Error: {e}")

    # 5. Timezone Hardening
    print("\n5. [Timezone Infrastructure]")
    now = get_utc_now()
    if timezone.is_aware(now):
        print(f"   [OK] System Time is Aware: {now}")
    else:
        print("   [FAIL] System Time is Naive")

    print("\n--- VERIFICATION COMPLETE ---")

if __name__ == "__main__":
    run_full_system_check()
