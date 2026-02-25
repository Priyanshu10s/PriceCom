import random
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from fake_useragent import UserAgent

# Attempt to import webdriver_manager, but don't crash if missing (assuming local driver or managed env)
try:
    from webdriver_manager.chrome import ChromeDriverManager
except ImportError:
    ChromeDriverManager = None

class HumanBehavior:
    """
    Simulates human-like interactions to evade detection.
    The 'Force' Logic for organic traffic simulation.
    """
    @staticmethod
    def smart_delay(min_seconds=2, max_seconds=5):
        """
        Randomized jitter to mimic human processing time.
        """
        sleep_time = random.uniform(min_seconds, max_seconds)
        time.sleep(sleep_time)

    @staticmethod
    def random_mouse_movement(driver, element):
        """
        Moves mouse to random offset within the element before clicking.
        """
        try:
            size = element.size
            width = size['width']
            height = size['height']
            
            # Random offset (avoiding edges)
            x_offset = random.randint(1, int(width * 0.8))
            y_offset = random.randint(1, int(height * 0.8))
            
            action = ActionChains(driver)
            action.move_to_element_with_offset(element, x_offset, y_offset).perform()
        except Exception:
            # Fallback to standard move
            pass

    @staticmethod
    def random_scroll(driver):
        """
        Scrolls up and down slightly to mimic reading.
        """
        try:
            scroll_amount = random.randint(100, 500)
            driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
            time.sleep(random.uniform(0.5, 1.5))
            # Occasional scroll back up
            if random.random() > 0.7:
                 driver.execute_script(f"window.scrollBy(0, -{random.randint(50, 150)});")
        except Exception:
            pass

class SeleniumStealthDriver:
    """
    Production-Ready Stealth Browser Factory.
    Configures Chrome to pass 'navigator.webdriver' checks and masks automation signals.
    """

    @staticmethod
    def get_driver(headless=True):
        """
        Returns a configured Chrome WebDriver with Stealth settings.
        """
        options = Options()
        ua = UserAgent()
        user_agent = ua.random
        
        # 1. User-Agent Rotation
        options.add_argument(f'user-agent={user_agent}')
        
        # 2. Advanced Stealth Configuration (The Force Logic)
        # Exclude automation switches
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Hide bot signature at browser level
        options.add_argument("--disable-blink-features=AutomationControlled")
        
        # 3. Production Optimization
        if headless:
            options.add_argument("--headless=new") # Modern headless mode
        
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        # Disable WebGL/RTC to prevent fingerprinting leaks
        # (Note: Some complex sites might need WebGL, but for scraping text/price, disabling is safer for stealth)
        options.add_argument("--disable-webgl")
        options.add_argument("--disable-webrtc")

        try:
            if ChromeDriverManager:
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=options)
            else:
                # Expect 'chromedriver' in PATH
                driver = webdriver.Chrome(options=options)
            
            # 4. JavaScript Injection (CDP Commands) - Critical for Anti-Bot
            # Manually set navigator.webdriver to undefined
            driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": """
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                """
            })
            
            return driver
            
        except Exception as e:
            print(f"[StealthBrowser] Error initializing driver: {e}")
            raise e

    @staticmethod
    def close_driver(driver):
        try:
            driver.quit()
        except:
            pass
