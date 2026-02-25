import abc
import logging
import time
import os
import re
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any, Optional, Union
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from core.utils.driver_factory import WebDriverFactory

logger = logging.getLogger(__name__)

class BaseScraper(abc.ABC):
    """
    Abstract Base Class for all scrapers.
    Implements the Template Method Pattern for the scraping workflow.
    Ensures resource management via Context Manager.
    """

    def __init__(self):
        self.driver: Optional[webdriver.Chrome] = None

    def __enter__(self):
        """
        Context Manager entry point. Initializes the WebDriver.
        """
        try:
            self.driver = WebDriverFactory.get_driver()
            return self
        except Exception as e:
            logger.error(f"Failed to initialize driver in Context Manager: {e}")
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context Manager exit point. Ensures the driver is quit strictly.
        """
        if self.driver:
            try:
                self.driver.quit()
                logger.info("WebDriver closed via Context Manager.")
            except Exception as e:
                logger.error(f"Error closing WebDriver in Context Manager: {e}")
        
        if exc_type:
            logger.error(f"Scraper exited with error: {exc_val}")

    def wait_for_element(self, selector: str, by: str = By.CSS_SELECTOR, timeout: int = 10) -> Optional[Any]:
        """
        Waits for an element to be present in the DOM.
        PRO-TIP: Use EC.presence_of_element_located for checking if element exists in DOM,
        vs EC.visibility_of_element_located if you need to interact with it.
        """
        if not self.driver:
            raise RuntimeError("Driver is not initialized.")
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, selector))
            )
        except TimeoutException:
            logger.warning(f"Timeout waiting for element: {selector}")
            return None

    def clean_price(self, price_str: str) -> Decimal:
        """
        Robust price cleaner. Removes currency symbols, commas, and whitespace.
        Returns Decimal('0.00') on failure.
        """
        if not price_str:
            return Decimal("0.00")
        
        # PRO-TIP: Keep only digits and the first decimal point.
        clean_str = re.sub(r'[^\d.]', '', price_str)
        try:
            return Decimal(clean_str)
        except Exception:
            logger.warning(f"Failed to convert price string '{price_str}' to Decimal.")
            return Decimal("0.00")

    def take_screenshot(self, filename: str):
        """
        Saves a screenshot to 'logs/screenshots/' for debugging failures.
        """
        if not self.driver:
            return

        directory = os.path.join("logs", "screenshots")
        os.makedirs(directory, exist_ok=True)
        filepath = os.path.join(directory, filename)
        
        try:
            self.driver.save_screenshot(filepath)
            logger.info(f"Screenshot saved to {filepath}")
        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")

    @abc.abstractmethod
    def get_title(self) -> Optional[str]:
        """Extract product title. Must be implemented by children."""
        pass

    @abc.abstractmethod
    def get_price(self) -> Optional[Decimal]:
        """Extract product price. Must be implemented by children."""
        pass

    def scrape(self, url: str) -> Dict[str, Any]:
        """
        Template Method: Defines the skeleton of the scraping operation.
        Includes Retry Logic for robustness.
        """
        attempts = 0
        max_retries = 3
        
        while attempts < max_retries:
            try:
                if not self.driver:
                    self.driver = WebDriverFactory.get_driver()

                logger.info(f"Scraping attempt {attempts + 1} for {url}")
                self.driver.get(url)
                
                # Basic standardized response structure
                data = {
                    "url": url,
                    "title": self.get_title(),
                    "price": self.get_price(),
                    "timestamp": datetime.now().isoformat(),
                    "status": "success"
                }
                
                if not data["title"] or not data["price"]:
                    logger.warning("Partial data extracted. Retrying might be needed.")
                
                return data

            except (TimeoutException, WebDriverException) as e:
                attempts += 1
                logger.warning(f"Attempt {attempts} failed: {e}")
                
                # Take screenshot on failure
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                self.take_screenshot(f"fail_{timestamp}_attempt_{attempts}.png")
                
                if attempts >= max_retries:
                    logger.error(f"Max retries reached for {url}.")
                    return {
                        "url": url,
                        "status": "failed",
                        "error": str(e),
                        "timestamp": datetime.now().isoformat()
                    }
                
                # Exponential Backoff
                time.sleep(2 ** attempts)
            
            except Exception as e:
                logger.exception(f"Critical error scraping {url}: {e}")
                return {
                    "url": url,
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
