import threading
from typing import List, Dict, Any, Optional
from datetime import timedelta
from django.utils import timezone
from django.db.models import Q
from decimal import Decimal

from apps.scraper.models import Product, StorePrice
from apps.scraper.concurrency import run_scraper_async
# Note: We need to import ScraperService carefully to avoid circular imports if it imports models
# But here we just need run_scraper_async which imports ScraperService. 

def get_coordinated_data(search_query: str) -> List[Dict[str, Any]]:
    """
    Orchestrates data retrieval:
    1. Search DB for products matching query.
    2. Check staleness of data (older than 6 hours).
    3. Trigger background scraping if data is stale.
    4. Returns current DB data immediately.
    """
    # 1. Search Database
    products = Product.objects.filter(name__icontains=search_query).prefetch_related('prices')
    
    results = []
    
    # Check for staleness logic
    six_hours_ago = timezone.now() - timedelta(hours=6)
    
    for product in products:
        product_data = {
            "name": product.name,
            "brand": product.brand,
            "category": product.category,
            "prices": []
        }
        
        for price in product.prices.all():
            # Add to results
            product_data["prices"].append({
                "store": price.store_name,
                "price": price.current_price,
                "url": price.product_url,
                "image": price.image_url,
                "available": price.is_available,
                "last_updated": price.last_updated
            })
            
            # 2. Check Staleness
            # Logic: If data is older than 6 hours, re-scrape.
            if price.last_updated < six_hours_ago:
                # 3. Trigger Background Scrape
                # We use threading to not block the user response.
                run_scraper_async(price.product_url, price.store_name)

        results.append(product_data)

    return results
