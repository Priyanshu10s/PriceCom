
import logging
import os
import random
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
    Includes Proxy Rotation and Stealth Flags.
    """
    
    # Simple Proxy List (In prod, fetch from API or Env)
    PROXY_LIST = [
        # "http://user:pass@1.2.3.4:8080", # Add real proxies here
    ]

    @staticmethod
    def get_driver() -> webdriver.Chrome:
        """
        Returns a fully configured Chrome WebDriver instance.
        """
        try:
            options = Options()
            
            # --- Stealth Settings ---
            # 1. Randomize User-Agent
            try:
                ua = UserAgent()
                user_agent = ua.random
            except Exception:
                user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            
            options.add_argument(f'user-agent={user_agent}')
            logger.info(f"Stealth Mode: Using User-Agent: {user_agent}")
            
            # 2. Prevent detection as automation
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # 3. Proxy Rotation
            if WebDriverFactory.PROXY_LIST:
                proxy = random.choice(WebDriverFactory.PROXY_LIST)
                options.add_argument(f'--proxy-server={proxy}')
                logger.info(f"Stealth Mode: Using Proxy: {proxy}")

            # --- Stability & Environment Settings ---
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage') # Overcome limited resource problems
            
            # --- Performance Settings ---
            # Disable images to speed up loading (Optional, depending on if images needed for validation)
            # options.add_argument('--blink-settings=imagesEnabled=false')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--log-level=3')

            # --- Headless Mode ---
            if os.getenv('SELENIUM_HEADLESS', 'True') == 'True':
                options.add_argument('--headless=new')
                # Stealth Fragment for Headless
                options.add_argument("--disable-gpu")
                
            # Initialize Service using webdriver_manager
            try:
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=options)
            except Exception as e:
                logger.warning(f"Failed to use webdriver_manager: {e}. Falling back to system driver.")
                # Fallback: Try using system-installed chromedriver (must be in PATH)
                driver = webdriver.Chrome(options=options)
            
            # --- Post-Init Stealth Scripts ---
            # Overwrite navigator.webdriver to undefined
            driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": """
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    })
                """
            })

            # Set explicit timeout
            timeout = int(os.getenv('SELENIUM_TIMEOUT', 30))
            driver.set_page_load_timeout(timeout)
            
            logger.info("Stealth WebDriver initialized successfully.")
            return driver

        except Exception as e:
            logger.error(f"Failed to initialize WebDriver: {e}")
            raise
