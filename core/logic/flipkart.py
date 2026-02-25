from typing import Optional
from decimal import Decimal
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import logging

from core.logic.base_scraper import BaseScraper
from core.selectors import StoreSelector

logger = logging.getLogger(__name__)

class FlipkartScraper(BaseScraper):
    """
    Concrete implementation for scraping Flipkart.
    Handles dynamic class names common in Flipkart's React/SPA structure.
    """

    def get_title(self) -> Optional[str]:
        # Flipkart uses classes like .B_NuCI or ._2NKhZn (older)
        # PRO-TIP: Use multiple selectors if the detailed one fails.
        selectors = [StoreSelector.FLIPKART["title"], "h1.B_NuCI", "h1._2NKhZn"]
        
        for sel in selectors:
            element = self.wait_for_element(sel, By.CSS_SELECTOR, timeout=3)
            if element:
                return element.text.strip()
        
        return None

    def get_price(self) -> Optional[Decimal]:
        # Flipkart price is usually in a div like ._30jeq3._16Jk6d
        element = self.wait_for_element(StoreSelector.FLIPKART["price"], By.CSS_SELECTOR)
        if element:
            return self.clean_price(element.text)
        
        logger.warning("Price element not found on Flipkart page.")
        return None

    # Note: Availability status extraction logic could be added here similar to price
    # e.g. def get_availability(self)...
