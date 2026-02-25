from typing import Optional
from decimal import Decimal
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import logging

from core.logic.base_scraper import BaseScraper
from core.selectors import StoreSelector

logger = logging.getLogger(__name__)

class AmazonScraper(BaseScraper):
    """
    Concrete implementation for scraping Amazon.
    Handles bot verification checks.
    """

    def get_title(self) -> Optional[str]:
        # Bot check: Sometimes Amazon asks for a captcha or just generic 'something went wrong'
        if "api-services-support@amazon.com" in self.driver.page_source:
             logger.warning("Amazon Bot Detection triggered.")
             return None

        # PRO-TIP: ID selectors are fastest.
        title_element = self.wait_for_element(StoreSelector.AMAZON["title"], By.CSS_SELECTOR)
        if title_element:
            return title_element.text.strip()
        return None

    def get_price(self) -> Optional[Decimal]:
        """
        Extracts price. Tries multiple selectors as Amazon changes layouts frequently.
        """
        # Primary selector
        price_element = self.wait_for_element(StoreSelector.AMAZON["price"], By.CSS_SELECTOR, timeout=5)
        
        if price_element:
            price_text = price_element.get_attribute("innerHTML") # Sometimes text is hidden
            # Fallback if innerHTML is empty (unlikely with this selector but possible)
            if not price_text:
                price_text = price_element.text
            return self.clean_price(price_text)
            
        # PRO-TIP: Fallback strategy for "Deal Price" vs "Regular Price"
        try:
            # Common alternative: 'span.a-price span.a-offscreen'
            # Check for deal price block specifically if main one fails
            deal_price = self.driver.find_element(By.CSS_SELECTOR, "#priceblock_dealprice")
            return self.clean_price(deal_price.text)
        except NoSuchElementException:
            pass

        logger.warning("Price element not found on Amazon page.")
        return None
