import os
import sys

# Configure environment for non-headless browser test
os.environ["SELENIUM_HEADLESS"] = "False"

# Setup Django standalone
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from core.services import ScraperService

def main():
    print("Initializing Scraper Service (Browser Mode)...")
    service = ScraperService()
    
    # Using a real Amazon India URL for iPhone 15 as per user's "iPhone 15" example intent
    # Note: Search-scraping requires a different logic (scraping search results page), 
    # but our current implementation scrapes product pages.
    url = "https://www.amazon.in/Apple-iPhone-15-128-GB/dp/B0CHX2F5QT"
    
    print(f"Opening Browser and Scraping: {url}")
    try:
        data = service.fetch_product_data(url, 'Amazon')
        print("\n--- Scraping Result ---")
        print(f"Success: {data.get('success')}")
        print(f"Name: {data.get('name')}")
        print(f"Price: {data.get('price')}")
        print(f"Store: {data.get('store')}")
        print(f"URL: {data.get('url')}")
        if data.get('error'):
             print(f"Error: {data.get('error')}")
        print("-----------------------")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
