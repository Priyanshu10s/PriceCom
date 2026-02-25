import os
import django
import sys
from decimal import Decimal

# Add project root to path
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.scraper.scraper_engine import ScraperFactory, ScraperEngine, ScrapeException
from apps.scraper.models import Product, Category

def run_verification():
    print("--- Scraper Architecture Verification ---")
    
    # 1. Test Price Cleaning
    print("[1] Testing Price Cleaning Logic")
    try:
        # Instantiate directly for unit test
        scraper = ScraperFactory.get_scraper("https://www.amazon.in/test")
        
        test_inputs = [
            ("₹1,299.00", Decimal("1299.00")),
            ("$19.99", Decimal("19.99")),
            ("50,000", Decimal("50000")),
            ("  ₹ 500  ", Decimal("500")),
        ]
        
        for raw, expected in test_inputs:
            cleaned = scraper.clean_price(raw)
            if cleaned == expected:
                print(f"   [OK] '{raw}' -> {cleaned}")
            else:
                print(f"   [FAIL] '{raw}' -> {cleaned} (Expected {expected})")
                
    except Exception as e:
        print(f"   [FAIL] Cleaning logic error: {e}")

    # 2. Test Factory Pattern
    print("\n[2] Testing Factory Pattern")
    amz = ScraperFactory.get_scraper("https://www.amazon.in/dp/123")
    flp = ScraperFactory.get_scraper("https://www.flipkart.com/p/123")
    
    print(f"   Amazon URL -> {amz.__class__.__name__}")
    print(f"   Flipkart URL -> {flp.__class__.__name__}")
    
    if "AmazonAdapter" in str(amz.__class__) and "FlipkartAdapter" in str(flp.__class__):
        print("   [OK] Factory returning correct adapters.")
    else:
        print("   [FAIL] Factory logic incorrect.")

    # 3. DB Sync Mock (Network dependent, so we verify the method existence/imports)
    print("\n[3] Testing DB Integration (Mock)")
    # Create test product
    cat, _ = Category.objects.get_or_create(name="ScraperTest")
    prod, _ = Product.objects.get_or_create(
        name="Scraper Test Product", 
        category=cat,
        defaults={'base_price': 100}
    )
    
    print(f"   Product ID: {prod.id} prepared for syncing.")
    
    # We won't actually call sync_to_db with a live URL to avoid huge Selenium overhead/failure in this script,
    # but we ensure the import and class Loading works.
    if hasattr(ScraperEngine, 'sync_to_db'):
         print("   [OK] ScraperEngine.sync_to_db is callable.")
    else:
         print("   [FAIL] ScraperEngine missing sync_to_db.")
    
    print("\n--- End Verification ---")

if __name__ == "__main__":
    run_verification()
