import os
import django
import sys
from django.template import Context, Template
from django.test import RequestFactory
import datetime
from django.utils import timezone

# Add project root to path
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.scraper.models import Product, Category, StorePrice

def run_ui_verification():
    print("--- UI Logic Verification ---")
    
    # Setup Data
    cat, _ = Category.objects.get_or_create(name='UITest')
    p = Product.objects.create(name="UI Item", category=cat)
    sp = StorePrice.objects.create(product=p, store_name='Amazon', current_price=100, product_url='http://test.com')
    
    # 1. Test Freshness Status Logic
    print("\n1. [Freshness Status Logic]")
    # status-live (<1hr)
    p.updated_at = timezone.now()
    p.save()
    status = p.get_freshness_status()
    print(f"   Now: {status}")
    if status == 'status-live': print("   [OK] status-live")
    else: print(f"   [FAIL] Expected status-live, got {status}")
    
    # status-delayed (<24hr)
    delayed_time = timezone.now() - datetime.timedelta(hours=5)
    Product.objects.filter(pk=p.pk).update(updated_at=delayed_time)
    p.refresh_from_db()
    status = p.get_freshness_status()
    print(f"   5hrs ago: {status}")
    if status == 'status-delayed': print("   [OK] status-delayed")
    else: print(f"   [FAIL] Expected status-delayed, got {status}")

    # status-stale (>24hr)
    stale_time = timezone.now() - datetime.timedelta(hours=25)
    Product.objects.filter(pk=p.pk).update(updated_at=stale_time)
    p.refresh_from_db()
    status = p.get_freshness_status()
    print(f"   25hrs ago: {status}")
    if status == 'status-stale': print("   [OK] status-stale")
    else: print(f"   [FAIL] Expected status-stale, got {status}")

    # 2. Template Rendering Simulation
    print("\n2. [Template Rendering]")
    from django.template.loader import get_template
    try:
        # Load template to check for syntax errors
        t = get_template('scraper/product_detail.html')
        print("   [OK] Template Syntax Valid")
    except Exception as e:
        print(f"   [FAIL] Template Syntax Error: {e}")

    # Cleanup
    sp.delete()
    p.delete()
    cat.delete()
    print("\n--- Verified ---")

if __name__ == "__main__":
    run_ui_verification()
