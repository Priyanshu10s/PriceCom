import logging
import datetime

logger = logging.getLogger(__name__)

class IntegrityGuardian:
    """
    The 'Integrity Guardian' Logger.
    Provides a high-fidelity audit trail for security events, demonstrating
    active System Integrity Monitoring (SIM).
    """

    @staticmethod
    def log_security_event(user_id: str, url: str, violation_type: str, details: str):
        """
        Logs a security violation with strict formatting for forensic analysis.
        Format: [SECURITY_ALERT] [INTEGRITY_VIOLATION] [USER_ID] [MALICIOUS_URL]
        """
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        # The specific format required for the 'Integrity Guardian'
        log_message = (
            f"[SECURITY_ALERT] [INTEGRITY_VIOLATION] "
            f"User: {user_id} | URL: {url} | Violation: {violation_type} | Details: {details} | Time: {timestamp}"
        )
        
        # Log to application logs (protected backend logs)
        logger.warning(log_message)
        
        # In a real 'Antigravity' system, we might also push this to a SIEM (e.g., Splunk/Datadog)
        # For now, standard logging proves the concept of an Audit Trail.

    @staticmethod
    def mask_internal_error(error: Exception) -> str:
        """
        The 'Data Privacy' Shield.
        Intercepts internal errors and returns a generic message to prevent
        Information Leakage (e.g., stack traces, paths).
        """
        # Log the full technical detail privately
        logger.error(f"[INTERNAL_EXCEPTION_SUPPRESSED] {str(error)}")
        
        # Return a sanitized message to the user/frontend
        return "Service Unavailable: The request was blocked by security policy."
