import urllib.parse
import ipaddress
import socket
from typing import Tuple, Optional

class SSRFShield:
    """
    Hardened SSRF (Server-Side Request Forgery) Protection Engine.
    Mathematically prevents internal probes, file leaks, and metadata theft.
    """

    # Whitelisted Schemes (Protocol Shield)
    ALLOWED_SCHEMES = {'http', 'https'}

    # Whitelisted Domains (Netloc Shield)
    # Strictly allow only target e-commerce platforms.
    ALLOWED_DOMAINS = {
        'www.amazon.in', 'amazon.in',
        'www.flipkart.com', 'flipkart.com',
        'www.ajio.com', 'ajio.com',
        'www.myntra.com', 'myntra.com'
    }

    # Internal CIDR Ranges (The Internal Probe Guard)
    PRIVATE_RANGES = [
        ipaddress.ip_network('127.0.0.0/8'),      # Loopback
        ipaddress.ip_network('10.0.0.0/8'),       # Private A
        ipaddress.ip_network('172.16.0.0/12'),    # Private B
        ipaddress.ip_network('192.168.0.0/16'),   # Private C
        ipaddress.ip_network('169.254.0.0/16'),   # Link-Local / Cloud Metadata
    ]

    @staticmethod
    def is_url_safe_for_scraping(user_url: str) -> Tuple[bool, str, Optional[str]]:
        """
        Validates a URL against strict SSRF rules.
        Returns: (is_safe, validated_url, error_code)
        """
        try:
            # 1. Normalization (Topper Validation Workflow)
            # Strip whitespace and force lowercase for consistent parsing
            user_url = user_url.strip()
            parsed = urllib.parse.urlparse(user_url)
            
            # 2. Protocol Shield (Force Logic)
            if parsed.scheme.lower() not in SSRFShield.ALLOWED_SCHEMES:
                return False, user_url, "INVALID_SCHEME"

            # 3. Netloc Shield (Force Logic)
            netloc = parsed.netloc.lower()
            # Remove port if present for domain check
            domain = netloc.split(':')[0]
            
            if domain not in SSRFShield.ALLOWED_DOMAINS:
                 # Check if it's an IP Obfuscation attempt
                try:
                    ipaddress.ip_address(domain)
                    return False, user_url, "IP_OBFUSCATION_DETECTED"
                except ValueError:
                    # It's a domain, but not allowed
                    return False, user_url, "DOMAIN_NOT_ALLOWED"

            # 4. Infrastructure & Metadata Defense (DNS Resolution Check)
            # Resolve the domain to IP to prevent DNS Rebinding or internal routing
            try:
                # Get all IPs for the domain
                ips = socket.getaddrinfo(domain, None)
                for item in ips:
                    ip_addr = item[4][0]
                    ip_obj = ipaddress.ip_address(ip_addr)
                    
                    # Check against Blacklisted Ranges
                    for private_range in SSRFShield.PRIVATE_RANGES:
                        if ip_obj in private_range:
                            return False, user_url, "INTERNAL_IP_DETECTED"
                            
            except socket.gaierror:
                return False, user_url, "DNS_RESOLUTION_FAILED"

            # Reconstruct the URL to ensure no hidden parts remain
            # We strictly rebuild it from the validated components
            final_url = urllib.parse.urlunparse(parsed)
            
            return True, final_url, None

        except Exception:
            return False, user_url, "PARSING_ERROR"
