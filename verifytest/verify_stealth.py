
import os
import django
import logging
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.scraper.stealth_engine import AdvancedScraperSession, HumanBehavior, RobotsComplianceManager

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_stealth_engine():
    print("--- Antigravity Stealth Verification ---")
    
    # 1. Test Header Forge
    print("\n[1] Testing Header Forge...")
    session_manager = AdvancedScraperSession()
    headers = session_manager.header_engine.get_random_headers()
    
    required_headers = ['User-Agent', 'sec-ch-ua', 'sec-ch-ua-platform']
    missing = [h for h in required_headers if h not in headers]
    
    if missing:
        print(f"[FAIL] Missing headers: {missing}")
    else:
        print("[PASS] Headers generated unsuccessfully.")
        print(f" -> User-Agent: {headers['User-Agent'][:50]}...")
        print(f" -> Platform: {headers['sec-ch-ua-platform']}")

    # 2. Test Robots Compliance
    print("\n[2] Testing Robots Compliance...")
    # Mocking a known site or just checking logic
    target_url = "https://www.amazon.in/dp/B09V7ZSQ27" 
    
    try:
        delay = session_manager.compliance_engine.get_crawl_delay(target_url)
        print(f"[PASS] Compliance Check: Crawl Delay = {delay}s")
    except Exception as e:
        print(f"[FAIL] Compliance Check Error: {e}")

    # 3. Test Jitter (Short)
    print("\n[3] Testing Jitter (Dry Run)...")
    try:
        HumanBehavior.human_like_delay(min_wait=0.1, max_wait=0.2)
        print("[PASS] Jitter executed without error.")
    except Exception as e:
         print(f"[FAIL] Jitter Error: {e}")

    print("\n--- Stealth Verification Complete ---")

if __name__ == "__main__":
    verify_stealth_engine()
