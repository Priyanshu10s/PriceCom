
import logging
import time
import random
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from apps.scraper.logic.base_scraper import BaseScraper

logger = logging.getLogger(__name__)

class StealthScraper(BaseScraper):
    """
    Advanced Scraper with Anti-Bot Evasion capabilities.
    Inherits from BaseScraper and adds:
    - Randomized Delays (Human-like behavior)
    - Robust Error Handling (Try-Except-Finally)
    - Stealth Actions
    """

    def random_sleep(self, min_seconds=2, max_seconds=5):
        """
        Pauses execution for a random interval to mimic human behavior.
        """
        sleep_time = random.uniform(min_seconds, max_seconds)
        logger.debug(f"Sleeping for {sleep_time:.2f} seconds...")
        time.sleep(sleep_time)

    def safe_find_element(self, selector: str, by: str = By.CSS_SELECTOR):
        """
        Robust element retrieval with error handling.
        Returns None if element not found, instead of crashing.
        """
        try:
            return self.driver.find_element(by, selector)
        except NoSuchElementException:
            logger.warning(f"Element not found: {selector}")
            return None
        except Exception as e:
            logger.error(f"Error finding element {selector}: {e}")
            return None

    def safe_get(self, url: str):
        """
        Navigate to URL with stealth checks and error handling.
        """
        try:
            logger.info(f"Navigating to {url}...")
            self.driver.get(url)
            self.random_sleep(3, 7) # Variance in load time
            
            # Stealth Check: Inject JS to remove webdriver property just in case
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
        except WebDriverException as e:
            logger.error(f"Navigation failed for {url}: {e}")
            return False
        return True

    def get_text_safe(self, selector: str) -> str:
        """
        Safely extracts text from an element.
        """
        element = self.safe_find_element(selector)
        if element:
            return element.text.strip()
        return ""
