import os
import django
import sys
from django.test import RequestFactory
from django.utils import timezone
import pytz

# Add project root to path
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.dashboard.middleware import TimezoneMiddleware

def run_tz_verification():
    print("--- IANA Timezone Engine Verification ---")
    
    factory = RequestFactory()
    
    # 1. Test No Cookie (Default UTC)
    print("\n1. [No Cookie] -> Should be UTC")
    request = factory.get('/')
    middleware = TimezoneMiddleware(lambda r: None)
    middleware(request)
    current_tz = timezone.get_current_timezone_name()
    print(f"   Current TZ: {current_tz}")
    if current_tz == 'UTC':
        print("   [OK] Defaulted to UTC")
    else:
        print(f"   [FAIL] Expected UTC, got {current_tz}")
        
    # 2. Test Valid Cookie (Asia/Kolkata)
    print("\n2. [Valid Cookie: Asia/Kolkata]")
    request = factory.get('/')
    request.COOKIES['django_timezone'] = 'Asia/Kolkata'
    middleware(request)
    current_tz = timezone.get_current_timezone_name()
    print(f"   Current TZ: {current_tz}")
    if current_tz == 'Asia/Kolkata':
        print("   [OK] Activated Asia/Kolkata")
    else:
        print(f"   [FAIL] Expected Asia/Kolkata, got {current_tz}")
        
    # 3. Test Invalid Cookie (Tampered)
    print("\n3. [Invalid Cookie: Mars/Phobos]")
    request = factory.get('/')
    request.COOKIES['django_timezone'] = 'Mars/Phobos'
    middleware(request)
    current_tz = timezone.get_current_timezone_name()
    print(f"   Current TZ: {current_tz}")
    if current_tz == 'UTC':
        print("   [OK] Fallback to UTC handled safely")
    else:
        print(f"   [FAIL] Security Fail-safe failed, got {current_tz}")

    print("\n--- Verified ---")

if __name__ == "__main__":
    run_tz_verification()
