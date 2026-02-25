import re
import logging
from decimal import Decimal, InvalidOperation
from abc import ABC, abstractmethod
from django.conf import settings
from django.utils import timezone
# Import models using apps.get_model to avoid potential circular imports
from django.apps import apps

# Local Imports
# Local Imports
from .stealth_browser import SeleniumStealthDriver, HumanBehavior
from .stealth_engine import AdvancedScraperSession, ScrapeException
from .security.handshake import SanitizationHandshake, UnsafeURLError

logger = logging.getLogger(__name__)

class ScraperBase(ABC):
    """
    Abstract Base Class for Scrapers.
    Enforces the Strategy Pattern and provides common utilities.
    Now integrated with Advanced Defensive Engineering.
    """
    
    def __init__(self, headless=True):
        self.session_manager = AdvancedScraperSession()
        self.driver = SeleniumStealthDriver.get_driver(headless=headless)
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        SeleniumStealthDriver.close_driver(self.driver)

    def pre_scrape_guard(self, url: str):
        """
        The Gatekeeper:
        1. Sanitization Handshake (SSRF + Integrity Check).
        2. Robots.txt Compliance.
        3. Jitter & Header Rotation.
        """
        # 1. Security Handshake (Deep-Trace Audit Requirement)
        # This blocks internal IPs, file://, and non-whitelisted domains.
        SanitizationHandshake.execute_sanitization_handshake(url, user_id="scraper_system")
        
        # 2. Compliance & Jitter (Sleeps here)
        # We use the session manager to handle the delay logic
        delay = self.session_manager.compliance_engine.get_crawl_delay(url)
        HumanBehavior.human_like_delay(min_wait=delay, max_wait=delay+2.0)
        
        # 3. Log intent
        logger.info(f"Guard: Accessing {url} with stealth protocols.")

    def clean_price(self, price_str: str) -> Decimal:
        """
        Robust Sanitizer: Extracts numeric price from strings like '₹1,299.00'.
        """
        try:
            # 1. Remove currency symbols and commas
            clean_str = re.sub(r'[^\d.]', '', price_str)
            return Decimal(clean_str)
        except (ValueError, InvalidOperation):
            raise ScrapeException(f"Failed to clean price: {price_str}")

    @abstractmethod
    def scrape_price(self, url: str) -> Decimal:
        """
        The Core Logic: Adapter must implement specific DOM parsing.
        """
        pass

class AmazonAdapter(ScraperBase):
    """Adapter for Amazon India."""
    
    def scrape_price(self, url: str) -> Decimal:
        try:
            # 1. Defensive Guard (Robots + Jitter)
            self.pre_scrape_guard(url)
            
            # 2. Access URL
            self.driver.get(url)
            HumanBehavior.random_scroll(self.driver)
            
            # Try multiple selectors (fallbacks)
            selectors = [
                'span.a-price-whole',
                'span#priceblock_ourprice',
                'span#priceblock_dealprice',
                'span.a-offscreen'
            ]
            
            price_text = None
            for selector in selectors:
                try:
                    element = self.driver.find_element("css selector", selector)
                    if element.is_displayed() or 'a-offscreen' in selector:
                        price_text = element.get_attribute("textContent") if 'a-offscreen' in selector else element.text
                        if price_text:
                            break
                except:
                    continue
            
            if not price_text:
                raise ScrapeException("Price element not found on Amazon page.")
                
            return self.clean_price(price_text)
            
        except Exception as e:
            logger.error(f"Amazon Scrape Error: {e}")
            raise ScrapeException(f"Amazon Scrape Failed: {e}")

class FlipkartAdapter(ScraperBase):
    """Adapter for Flipkart."""
    
    def scrape_price(self, url: str) -> Decimal:
        try:
            # 1. Defensive Guard (Robots + Jitter)
            self.pre_scrape_guard(url)
            
            # 2. Access URL
            self.driver.get(url)
            HumanBehavior.random_scroll(self.driver)
            
            # Flipkart usually puts price in div.Nx9bqj.CxhGGd (class names change frequently)
            # Strategy: Look for currency symbol or reliable classes
            selectors = [
                'div._30jeq3', # Common Flipkart price class
                'div.Nx9bqj', # Newer class
                'div._30jeq3._16Jk6d'
            ]
            
            price_text = None
            for selector in selectors:
                try:
                    element = self.driver.find_element("css selector", selector)
                    price_text = element.text
                    if price_text:
                        break
                except:
                    continue

            if not price_text:
                raise ScrapeException("Price element not found on Flipkart page.")
                
            return self.clean_price(price_text)

        except Exception as e:
            logger.error(f"Flipkart Scrape Error: {e}")
            raise ScrapeException(f"Flipkart Scrape Failed: {e}")

class GenericAdapter(ScraperBase):
    """Fallback Adapter for other sites."""
    
    def scrape_price(self, url: str) -> Decimal:
        # Placeholder for generic logic or meta tag parsing
        raise ScrapeException("Generic scraping not yet implemented.")

class ScraperFactory:
    """
    Factory to return the correct Adapter based on URL.
    """
    @staticmethod
    def get_scraper(url: str):
        if "amazon" in url:
            return AmazonAdapter()
        elif "flipkart" in url:
            return FlipkartAdapter()
        else:
            return GenericAdapter()

class ScraperEngine:
    """
    The Bridge: Connects Scraper Logic to Django Database.
    """
    
    @staticmethod
    def sync_to_db(product_id: int, url: str):
        """
        Syncs scrapped price to the database.
        1. Scrapes price.
        2. Updates Product model.
        3. Creates PriceHistory (Signal handles analytics).
        """
        Product = apps.get_model('scraper', 'Product')
        PriceHistory = apps.get_model('scraper', 'PriceHistory')
        StorePrice = apps.get_model('scraper', 'StorePrice')
        
        try:
            scraper = ScraperFactory.get_scraper(url)
            
            with scraper as s:
                price = s.scrape_price(url)
                
            # Database Update
            product = Product.objects.get(pk=product_id)
            
            # Find or Create StorePrice (assuming URL maps to a store variant)
            # For simplicity in this function, we assume a StorePrice exists or we update the primary
            # In a real multi-variant system, we'd pass store_price_id. 
            # Here, let's update the first matching StorePrice or create one.
            domain = "Amazon" if "amazon" in url else "Flipkart"
            
            store_price, created = StorePrice.objects.get_or_create(
                product=product,
                store_name=domain,
                defaults={'product_url': url, 'current_price': price}
            )
            
            # Update Current Price
            store_price.current_price = price
            store_price.last_updated = timezone.now()
            store_price.save()
            
            # Create History (Signal will handle trends/hashing)
            PriceHistory.objects.create(
                store_price=store_price,
                price=price
            )
            
            # Update Product aggregate (lowest price)
            product.current_lowest_price = price # Simplified logic
            product.save()
            
            return price
            
        except ScrapeException as e:
            logger.warning(f"Scrape Warning: {e}")
            # Logic to mark product as "Check Layout" could go here
            return None
        except Exception as e:
            logger.error(f"Critical Scraper Error: {e}")
            return None
