import re
from urllib.parse import urlparse, urlunparse
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class SecurityShield:
    """
    Topper Grade Cybersecurity Shield Layer.
    Protects against malformed URLs, SSRF, and XSS.
    """

    ALLOWED_DOMAINS = ['www.amazon.in', 'www.amazon.com', 'www.flipkart.com', 'flipkart.com']

    @staticmethod
    def sanitize_product_url(url: str) -> Optional[str]:
        """
        Input Sanitization: Strips tracking parameters (UTMs), session IDs, 
        and ensures the URL attacks only whitelisted domains.
        """
        if not url:
            return None
            
        try:
            parsed = urlparse(url)
            
            # SSRF Protection: Strict Domain Whitelist
            if parsed.netloc not in SecurityShield.ALLOWED_DOMAINS:
                logger.warning(f"SSRF Prevention: Blocked non-whitelisted domain {parsed.netloc}")
                return None
                
            # Strip all query strings (UTMs, tracking) to ensure clean DB storage
            # Note: For Flipkart, 'pid' is required. So we selectively keep it.
            clean_query = ""
            if 'flipkart' in parsed.netloc:
                match = re.search(r'pid=([A-Z0-9]+)', parsed.query)
                if match:
                     clean_query = f"pid={match.group(1)}"
                     
            clean_parsed = parsed._replace(query=clean_query, fragment='')
            return urlunparse(clean_parsed)
            
        except Exception as e:
            logger.error(f"URL Sanitization Failed: {e}")
            return None
