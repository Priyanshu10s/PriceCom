import logging
import hashlib
from typing import Dict, Optional, Any
from decimal import Decimal
from datetime import datetime

from apps.scraper.logic.amazon import AmazonScraper
from apps.scraper.logic.flipkart import FlipkartScraper
from apps.scraper.models import Product, StorePrice

logger = logging.getLogger(__name__)

class ScraperService:
    """
    Service layer that orchestrates the scraping process.
    Delegates the actual scraping to store-specific implementations (Framework).
    Handles data persistence.
    """

    def _get_scraper_class(self, store_name: str):
        if store_name.lower() == 'amazon':
            return AmazonScraper
        elif store_name.lower() == 'flipkart':
            return FlipkartScraper
        else:
            raise ValueError(f"No scraper implementation found for store: {store_name}")

    def fetch_product_data(self, url: str, store_name: str) -> Dict[str, Any]:
        """
        Fetches product data using the appropriate Scraper class.
        """
        logger.info(f"Initiating scrape for {url} on {store_name}")
        
        try:
            ScraperClass = self._get_scraper_class(store_name)
            
            # Use Context Manager to ensure driver is handled correctly
            with ScraperClass() as scraper:
                data = scraper.scrape(url)
                
            # Normalize keys if necessary (BaseScraper returns 'title', 'price', 'status')
            data["store"] = store_name
            data["success"] = data.get("status") == "success"
            # Map 'title' to 'name' for consistency with internal logic if needed, 
            # though save_product below can just use 'title'
            data["name"] = data.get("title") 
            
            return data

        except Exception as e:
            logger.exception(f"Error during scraping execution: {e}")
            return {
                "url": url,
                "store": store_name,
                "success": False,
                "error": str(e)
            }

    def save_product(self, data: Dict[str, Any]) -> Optional[Product]:
        """
        Saves the scraped data to the database using the new normalized schema.
        """
        if not data.get("success"):
            logger.warning(f"Skipping save for failed scrape: {data.get('url')}")
            return None
        
        try:
            # 1. Update/Create Product (Meta)
            product, created = Product.objects.get_or_create(
                name=data.get("name") or "Unknown Product",
                defaults={
                    "brand": "Unknown", # Needs logic or parsing
                    "category": "Uncategorized"
                }
            )
            
            # 2. Update/Create StorePrice
            # Ensure price is a Decimal
            price_val = data.get("price")
            if price_val is None:
                 price_val = Decimal("0.00")

            # Data Integrity Hash
            # Hash = SHA256(price_str + timestamp_str + secret_salt)
            timestamp = datetime.now().isoformat()
            raw_data = f"{price_val}{timestamp}{'SUPER_SECRET_SALT'}"
            price_hash = hashlib.sha256(raw_data.encode()).hexdigest()

            price_obj, price_created = StorePrice.objects.update_or_create(
                product=product,
                store_name=data["store"],
                defaults={
                    "current_price": price_val,
                    "product_url": data["url"],
                    "image_url": data.get("image_url", ""), # BaseScraper might not extract image yet, handled in cleanup
                    "is_available": True,
                    "price_hash": price_hash
                }
            )
            # 3. Create PriceHistory with Signature
            # Import strictly here or top level
            from apps.scraper.models import PriceHistory
            from apps.scraper.security_utils import generate_signature
            from django.conf import settings
            
            # Data to sign (Deterministic for verification)
            history_data = {
                'price': str(price_val),
                'currency': 'INR'
            }
            signature = generate_signature(settings.SECRET_KEY, history_data)
            
            PriceHistory.objects.create(
                store_price=price_obj,
                price=price_val,
                currency='INR',
                data_signature=signature
            )

            logger.info(f"Product saved successfully: {product.name}")
            return product
            
        except Exception as e:
            logger.error(f"Failed to save product data: {e}")
            return None

    def search_products(self, query: str, store_name: str) -> list[Dict[str, Any]]:
        """
        Searches for products on the specified store and returns a list of results (URLs/Basic Info).
        """
        logger.info(f"Searching for '{query}' on {store_name}")
        
        try:
            ScraperClass = self._get_scraper_class(store_name)
            
            with ScraperClass() as scraper:
                # We need to implement get_search_results in the specific scraper classes
                if hasattr(scraper, 'get_search_results'):
                     results = scraper.get_search_results(query)
                else:
                    logger.warning(f"{store_name} scraper does not support search.")
                    results = []
            
            return results

        except Exception as e:
            logger.exception(f"Error during search execution on {store_name}: {e}")
            return []

    def find_cheaper_alternative(self, product_name: str, current_price: Decimal, exclude_store: str) -> Dict[str, Any]:
        """
        Cross-Store Analysis Hook.
        Performs a secondary 'Quick Search' on competing platforms.
        If a lower price is found, returns the link and savings amount.
        """
        stores = ['Amazon', 'Flipkart']
        target_store = next((s for s in stores if s.lower() != exclude_store.lower()), 'Amazon')
        
        logger.info(f"Cross-Store Analysis: Searching for '{product_name}' on {target_store}")
        
        results = self.search_products(product_name, target_store)
        
        # This is a naive heuristic (first result). In production, 
        # ML product matching would be used.
        if results:
            best_match = results[0]
            compare_price = Decimal(str(best_match.get('price', 0)))
            
            if compare_price > 0 and compare_price < current_price:
                savings = current_price - compare_price
                return {
                    "found": True,
                    "cheaper_link": best_match.get('url'),
                    "savings_amount": float(savings),
                    "store": target_store,
                    "price": float(compare_price)
                }
                
        return {"found": False}
