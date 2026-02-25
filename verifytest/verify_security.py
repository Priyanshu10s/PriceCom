
import os
import django
import logging
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.scraper.security.handshake import SanitizationHandshake, UnsafeURLError
from apps.scraper.security.ssrf_shield import SSRFShield

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_defense_depth():
    print("--- Antigravity Defense-in-Depth Verification ---")
    
    # Test Cases: [URL, Expected Result]
    test_cases = [
        ("https://www.amazon.in/dp/B09V7ZSQ27", True),     # Safe: Amazon
        ("http://www.flipkart.com/some-product", True),     # Safe: Flipkart
        ("ftp://www.amazon.in/file", False),                # Unsafe: Protocol (FTP)
        ("file:///etc/passwd", False),                      # Unsafe: Protocol (File)
        ("https://127.0.0.1/admin", False),                 # Unsafe: IP (Localhost)
        ("http://169.254.169.254/latest/meta-data/", False),# Unsafe: IP (Cloud Metadata)
        ("https://google.com", False),                      # Unsafe: Domain (Not Whitelisted)
        ("  https://www.AMAZON.in/dp/Ref  ", True),         # Safe: Normalization Needed
    ]

    print(f"\n[1] Running {len(test_cases)} Vectors through Sanitization Handshake...")
    
    passed_count = 0
    for url, should_pass in test_cases:
        try:
            # Execute Handshake
            safe_url = SanitizationHandshake.execute_sanitization_handshake(url, user_id="test_user")
            
            if should_pass:
                print(f"[PASS] Allowed Safe URL: {url[:40]}...")
                passed_count += 1
            else:
                print(f"[FAIL] Security Breach! Allowed Unsafe URL: {url}")
                
        except UnsafeURLError as e:
            if not should_pass:
                print(f"[PASS] Blocked Unsafe URL: {url[:40]}... Reason: {e}")
                passed_count += 1
            else:
                 print(f"[FAIL] False Positive! Blocked Safe URL: {url} Reason: {e}")
        except Exception as e:
            print(f"[ERROR] Logic Crash on {url}: {e}")

    print(f"\n[2] Verification Score: {passed_count}/{len(test_cases)}")
    
    if passed_count == len(test_cases):
        print(" -> SECURITY STATUS: BULLETPROOF (Antigravity Grade)")
    else:
        print(" -> SECURITY STATUS: VULNERABLE (Check Logs)")

    print("\n--- Integrity Audit Check ---")
    print("Check 'apps/scraper/logs' or console output for [SECURITY_ALERT] entries.")

if __name__ == "__main__":
    verify_defense_depth()
