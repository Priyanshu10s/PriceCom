import logging
from typing import Dict, Optional, Any
from decimal import Decimal

from core.logic.amazon import AmazonScraper
from core.logic.flipkart import FlipkartScraper
from core.models import Product, StorePrice

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

            price_obj, price_created = StorePrice.objects.update_or_create(
                product=product,
                store_name=data["store"],
                defaults={
                    "current_price": price_val,
                    "product_url": data["url"],
                    "image_url": data.get("image_url", ""), # BaseScraper might not extract image yet, handled in cleanup
                    "is_available": True 
                }
            )
            
            logger.info(f"Product saved successfully: {product.name}")
            return product
            
        except Exception as e:
            logger.error(f"Failed to save product data: {e}")
            return None
