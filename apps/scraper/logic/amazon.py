from typing import Optional
from decimal import Decimal
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import logging

from apps.scraper.logic.stealth_scraper import StealthScraper
from apps.scraper.selectors import StoreSelector

logger = logging.getLogger(__name__)

class AmazonScraper(StealthScraper):
    """
    Concrete implementation for scraping Amazon.
    Inherits from StealthScraper for anti-bot capabilities.
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

    def get_search_results(self, query: str) -> list[dict]:
        """
        Searches Amazon for the query and returns list of product info.
        """
        search_url = f"https://www.amazon.in/s?k={query.replace(' ', '+')}"
        search_results = []
        
        try:
            self.driver.get(search_url)
            # Wait for results to load
            self.wait_for_element("div[data-component-type='s-search-result']", By.CSS_SELECTOR)
            
            product_cards = self.driver.find_elements(By.CSS_SELECTOR, "div[data-component-type='s-search-result']")
            
            # Limit to top 5 results to save time
            for card in product_cards[:5]:
                try:
                    # Extract ASIN or URL
                    # Amazon usually puts the link on the title h2 a
                    link_element = card.find_element(By.CSS_SELECTOR, "h2 a.a-link-normal")
                    url = link_element.get_attribute("href")
                    title = link_element.text
                    
                    if url and "https" in url:
                         search_results.append({
                             "store": "Amazon",
                             "name": title,
                             "url": url,
                             # We can try to grab price/image here too if needed for preview
                         })
                except Exception as e:
                    logger.warning(f"Error parsing Amazon search card: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error searching Amazon: {e}")
            
        return search_results
