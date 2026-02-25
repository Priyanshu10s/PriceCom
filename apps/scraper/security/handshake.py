import logging
import urllib.parse
from typing import Optional
from .ssrf_shield import SSRFShield
from .integrity import IntegrityGuardian

logger = logging.getLogger(__name__)

class UnsafeURLError(Exception):
    """Custom Exception for Security Violations during Handshake."""
    pass

class SanitizationHandshake:
    """
    The 'Sanitization Handshake' Protocol.
    A multi-stage security gateway that purifies user-provided URLs before
    they reach the scraping engine.
    """

    @staticmethod
    def execute_sanitization_handshake(raw_url: str, user_id: str = "system") -> str:
        """
        Executes the full security pipeline.
        
        Stage 1: Normalization
        Stage 2: Structural Parsing & Whitelist Validation (SSRF Shield)
        Stage 3: Integrity Logging on Failure
        Stage 4: Terminal Guard (Block/Allow)
        """
        try:
            # Stage 1: Normalization (The "Topper" Standard)
            # Remove leading/trailing whitespace
            clean_url = raw_url.strip()
            
            # Stage 2: Structural Parsing & Whitelist Validation
            # Delegate mathematical validation to the SSRF Shield
            is_safe, validated_url, error_code = SSRFShield.is_url_safe_for_scraping(clean_url)
            
            if not is_safe:
                # Stage 3: Integrity Logging
                # Log the specific violation for forensic audit
                IntegrityGuardian.log_security_event(
                    user_id=user_id,
                    url=clean_url,
                    violation_type=f"SSRF_BLOCK_{error_code}",
                    details="Handshake Failed: Domain/IP/Protocol violation detected."
                )
                
                # Stage 4: Terminal Guard
                raise UnsafeURLError(f"Security Handshake Failed: {error_code}")

            # Return the "Safe Handle" (Validated URL)
            return validated_url

        except UnsafeURLError:
            raise
        except Exception as e:
            # Catch-all for parsing bombs or unexpected errors
            IntegrityGuardian.log_security_event(
                user_id=user_id,
                url=raw_url,
                violation_type="HANDSHAKE_CRASH",
                details=str(e)
            )
            # Mask the internal error
            raise UnsafeURLError("Security Handshake Failed: Internal Processing Error")

    @staticmethod
    def secure_get_request(url: str, session=None, **kwargs):
        """
        The 'Secure-Fetch' Wrapper.
        Forces every URL through the Handshake before the requests.get() call.
        """
        # 1. Force Handshake
        safe_url = SanitizationHandshake.execute_sanitization_handshake(url)
        
        # 2. Execute Request (using provided session or requests lib)
        if session:
            return session.get(safe_url, **kwargs)
            
        import requests
        return requests.get(safe_url, **kwargs)
