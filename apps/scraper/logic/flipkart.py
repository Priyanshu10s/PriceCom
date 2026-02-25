from typing import Optional
from decimal import Decimal
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import logging

from apps.scraper.logic.stealth_scraper import StealthScraper
from apps.scraper.selectors import StoreSelector

logger = logging.getLogger(__name__)

class FlipkartScraper(StealthScraper):
    """
    Concrete implementation for scraping Flipkart.
    Inherits from StealthScraper for anti-bot capabilities.
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

        return None

    # Note: Availability status extraction logic could be added here similar to price
    # e.g. def get_availability(self)...

    def get_search_results(self, query: str) -> list[dict]:
        search_url = f"https://www.flipkart.com/search?q={query.replace(' ', '%20')}"
        search_results = []
        
        try:
            self.driver.get(search_url)
            # Flipkart results usually are in div._1AtVbE or div._13oc-S (grid)
            # We wait for the container
            self.wait_for_element("div._1AtVbE", By.CSS_SELECTOR)
            
            # Common class for product container in list view: div._1AtVbE 
            # But inside that: a._1fQZEK (mobile phones/electronics usually) or a.s1Q9rs (smaller items)
            # Let's try flexible selection
            cards = self.driver.find_elements(By.CSS_SELECTOR, "div._1AtVbE")
            
            count = 0
            for card in cards:
                if count >= 5: break
                
                try:
                    # Try finding the anchor tag with href
                    # Standard list view
                    anchors = card.find_elements(By.CSS_SELECTOR, "a._1fQZEK")
                    if not anchors:
                        # Grid view style
                        anchors = card.find_elements(By.CSS_SELECTOR, "a.s1Q9rs")
                    
                    if not anchors:
                        # Fallback generic
                         anchors = card.find_elements(By.TAG_NAME, "a")
                         
                    for a in anchors:
                         href = a.get_attribute("href")
                         title = ""
                         
                         # Try to find title div
                         try:
                             title_div = a.find_element(By.CSS_SELECTOR, "div._4rR01T") # List view title
                             title = title_div.text
                         except:
                             try:
                                title = a.get_attribute("title")
                             except:
                                pass
                         
                         if href and "/p/" in href: # Valid product link usually has /p/
                             search_results.append({
                                 "store": "Flipkart",
                                 "name": title or "Flipkart Product",
                                 "url": href
                             })
                             count += 1
                             if count >= 5: break
                except Exception:
                    continue
                    
        except Exception as e:
            logger.error(f"Error searching Flipkart: {e}")
            
        return search_results
