import os
import django
import sys
import datetime
from django.utils import timezone
from django.template import Context, Template

# Add project root to path
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.scraper.models import Product, Category
from apps.dashboard.context_processors import server_time

def run_sync_verification():
    print("--- Time Sync Architecture Verification ---")

    # 1. Product Model Hardening
    print("\n1. [Product Model Hardening]")
    cat, _ = Category.objects.get_or_create(name='SyncTest')
    
    # Test Naive Injection
    naive_dt = datetime.datetime.now()
    p = Product(name="Naive Test", category=cat)
    # Manually setting updated_at to naive (simulating bad input)
    p.updated_at = naive_dt 
    p.save()
    
    p.refresh_from_db()
    if timezone.is_aware(p.updated_at):
        print(f"   [OK] Naive timestamp auto-converted to Aware: {p.updated_at}")
    else:
        print(f"   [FAIL] Timestamp remained Naive: {p.updated_at}")
        
    # 2. get_exact_sync_diff
    print("\n2. [Sync Diff Calculation]")
    diff = p.get_exact_sync_diff()
    print(f"   Sync Diff: {diff}")
    if isinstance(diff, datetime.timedelta):
         print("   [OK] Returned Valid Timedelta")
    else:
         print("   [FAIL] Invalid Return Type")

    # 3. Context Processor
    print("\n3. [Context Processor]")
    from django.test import RequestFactory
    factory = RequestFactory()
    request = factory.get('/')
    ctx = server_time(request)
    print(f"   Context Data: {ctx}")
    if 'server_now' in ctx and timezone.is_aware(ctx['server_now']):
         print("   [OK] Server Time Injected & Aware")
    else:
         print("   [FAIL] Context Processor Failed")

    # Cleanup
    p.delete()
    cat.delete()
    print("\n--- Verified ---")

if __name__ == "__main__":
    run_sync_verification()
