import logging
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent

logger = logging.getLogger(__name__)

class WebDriverFactory:
    """
    Factory class to create fully configured Selenium WebDriver instances.
    Compatible with Windows (Local) and Linux (Production).
    """

    @staticmethod
    def get_driver() -> webdriver.Chrome:
        """
        Returns a fully configured Chrome WebDriver instance.
        """
        try:
            options = Options()
            
            # --- Stealth Settings ---
            # Randomize User-Agent
            ua = UserAgent()
            user_agent = ua.random
            options.add_argument(f'user-agent={user_agent}')
            
            # Prevent detection as automation
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)

            # --- Stability & Environment Settings ---
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage') # Overcome limited resource problems
            options.add_argument('--disable-gpu') # Applicable to windows os only
            
            # --- Performance Settings ---
            # Disable images to speed up loading
            options.add_argument('--blink-settings=imagesEnabled=false')
            options.add_argument('--window-size=1920,1080')

            # --- Headless Mode ---
            if os.getenv('SELENIUM_HEADLESS', 'True') == 'True':
                options.add_argument('--headless=new')

            # Initialize Service using webdriver_manager
            try:
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=options)
            except Exception as e:
                logger.warning(f"Failed to use webdriver_manager: {e}. Falling back to system driver.")
                # Fallback: Try using system-installed chromedriver (must be in PATH)
                driver = webdriver.Chrome(options=options)
            
            # Set explicit timeout
            timeout = int(os.getenv('SELENIUM_TIMEOUT', 20))
            driver.set_page_load_timeout(timeout)
            
            logger.info("WebDriver initialized successfully.")
            return driver

        except Exception as e:
            logger.error(f"Failed to initialize WebDriver: {e}")
            raise
