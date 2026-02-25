import random
import time
import requests
import logging
import urllib.robotparser
from urllib.parse import urlparse
from fake_useragent import UserAgent

logger = logging.getLogger(__name__)

class HumanBehavior:
    """
    Simulates human-like interactions to evade detection.
    The 'Force' Logic for organic traffic simulation.
    """
    
    @staticmethod
    def human_like_delay(min_wait: float = 2.0, max_wait: float = 7.0):
        """
        Randomized Jitter Engine.
        Creates "Temporal Entropy" to break the mathematical signature of a bot.
        """
        delay = random.uniform(min_wait, max_wait)
        logger.info(f"Human Jitter: Sleeping for {delay:.2f} seconds...")
        time.sleep(delay)

    @staticmethod
    def jitter():
        """Legacy wrapper for human_like_delay"""
        HumanBehavior.human_like_delay()

class StealthHeaderEngine:
    """
    High-End Stealth Header Engine & Identity Vault.
    Generates production-ready, randomized headers to bypass anti-bot systems.
    """
    
    # The Identity Vault: Curated Pool of Modern User Agents (2024-2025)
    USER_AGENT_POOL = [
        # Windows 11 / Chrome 120+
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        # macOS / Safari
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
        # Firefox
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
    ]

    def __init__(self):
        self.current_identity = None

    def get_random_headers(self) -> dict:
        """
        High-Fidelity Header Forge.
        Generates consistent headers including Sec-Ch-Ua, matching the User-Agent.
        """
        # Session Sticky Logic: Reuse identity if set, else pick new
        if not self.current_identity:
            self.current_identity = random.choice(self.USER_AGENT_POOL)
            
        user_agent = self.current_identity
        
        # Strategic Referer Selection
        referers = [
            "https://www.google.com/",
            "https://www.bing.com/",
            "https://duckduckgo.com/",
            "https://www.amazon.in/", # Internal nav simulation
        ]
        
        headers = {
            # Standard Browser Order (Chrome-like)
            'Host': 'www.amazon.in', # Placeholder, usually set by lib but good for spoofing if needed
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'document',
            'Referer': random.choice(referers),
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            
            # SEC Headers (Mocking Chrome on Windows)
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }
        
        # Cleanup Host if generic
        if headers['Host'] == 'www.amazon.in': 
            del headers['Host']
            
        return headers

class RobotsComplianceManager:
    """
    The "Robots.txt" Compliance Guardian.
    Ensures ethical crawling by respecting site-specific rules.
    """
    
    def __init__(self):
        self.parser = urllib.robotparser.RobotFileParser()
        self.domain_cache = {} # Cache delay per domain

    def get_crawl_delay(self, url: str) -> float:
        """
        Fetches robots.txt and extracts Crawl-delay.
        Defaults to safe 2-second buffer ("Professional Ethics").
        """
        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        robots_url = f"{base_url}/robots.txt"
        
        if base_url in self.domain_cache:
            return self.domain_cache[base_url]
            
        try:
            logger.info(f"Checking robots.txt for {base_url}")
            self.parser.set_url(robots_url)
            self.parser.read()
            
            delay = self.parser.crawl_delay("*")
            if not delay:
                delay = 2.0 # Default Safe Buffer
                
            logger.info(f"Compliance: Crawl-delay for {parsed_url.netloc} is {delay}s")
            self.domain_cache[base_url] = float(delay)
            return float(delay)
            
        except Exception as e:
            logger.warning(f"Robots.txt check failed for {base_url}: {e}. Defaulting to 2s.")
            return 2.0

class AdvancedScraperSession:
    """
    The Integrated Session Manager.
    Bundles Headers, Jitter, and Backoff into a single 'Antigravity' unit.
    """
    
    def __init__(self):
        self.header_engine = StealthHeaderEngine()
        self.compliance_engine = RobotsComplianceManager()
        self.session = requests.Session()
        
    def fetch_page(self, url: str):
        """
        Self-Aware Fetcher with Exponential Backoff.
        """
        # 1. Apply Compliance Delay
        required_delay = self.compliance_engine.get_crawl_delay(url)
        
        # 2. Add Entropy (Jitter)
        # We add jitter ON TOP of the required delay for max stealth
        jitter = random.uniform(0.5, 2.0)
        total_wait = required_delay + jitter
        
        logger.info(f"Sleeping {total_wait:.2f}s (Compliance={required_delay} + Entropy={jitter:.2f})")
        time.sleep(total_wait)
        
        # 3. Rotate/Set Headers
        headers = self.header_engine.get_random_headers()
        self.session.headers.update(headers)
        
        # 4. Resilience Loop (Exponential Backoff)
        max_retries = 3
        backoff_factor = 2
        
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, timeout=15)
                
                # Check 429 (Too Many Requests) or 503 (Service Unavailable)
                if response.status_code in [429, 503]:
                    retry_after = response.headers.get("Retry-After")
                    if retry_after:
                        wait_time = int(retry_after)
                    else:
                        wait_time = backoff_factor ** attempt * 5 # 5, 10, 20s
                        
                    logger.warning(f"Hit {response.status_code}. Backing off for {wait_time}s...")
                    time.sleep(wait_time)
                    
                    # Refresh Identity ("New User" simulation)
                    self.header_engine.current_identity = None 
                    self.session.headers.update(self.header_engine.get_random_headers())
                    continue
                    
                return response
                
            except Exception as e:
                logger.error(f"Request failed: {e}")
                time.sleep(backoff_factor ** attempt)
                
        return None
