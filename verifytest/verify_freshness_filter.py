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

from apps.dashboard.templatetags.freshness_filters import smart_freshness

def run_filter_verification():
    print("--- Freshness Filter Verification ---")
    
    now = timezone.now()
    
    # Case 1: Just Now (< 30s)
    just_now_time = now - datetime.timedelta(seconds=15)
    result_jn = smart_freshness(just_now_time)
    print(f"1. Testing 15s ago: {result_jn}")
    if "Just now" in result_jn and "text-successGreen" in result_jn:
        print("   [OK] Correctly identified 'Just now'")
    else:
        print("   [FAIL] Content mismatch")

    # Case 2: Standard (> 30s)
    old_time = now - datetime.timedelta(minutes=5)
    result_old = smart_freshness(old_time)
    print(f"2. Testing 5m ago: {result_old}")
    if "minutes ago" in result_old and "span" not in result_old:
         print("   [OK] Correctly delegated to naturaltime")
    else:
         print("   [FAIL] Content mismatch or unexpected HTML")
         
    # Case 3: Future (Clock Skew Protection)
    future_time = now + datetime.timedelta(seconds=5)
    result_future = smart_freshness(future_time)
    print(f"3. Testing 5s in future: {result_future}")
    if "Just now" in result_future:
        print("   [OK] Latency Shield Works (Future treated as Just Now)")
    else:
        print("   [FAIL] Future time not handled correctly")

    print("\n--- Verified ---")

if __name__ == "__main__":
    run_filter_verification()
