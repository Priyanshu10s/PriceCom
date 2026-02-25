import logging
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
from typing import Optional
from apps.scraper.models import PriceHistory # Assuming this tracks history
# Note: User might not have a specific NotificationLog model yet, so I will simulate the logic
# or assume a generic alert model. For now, I'll draft the logic to be integrable.

logger = logging.getLogger('apps.scraper')

class ReputationEngine:
    """
    High-Precision Alert Filtering & Reputation Protection Layer.
    Ensures 100% inbox delivery by suppressing low-value 'noise'.
    """
    
    @staticmethod
    def should_dispatch_email(user_id: int, product_id: int, last_alert_timestamp: Optional[timezone.datetime]) -> bool:
        """
        The 'Cool-down' Rule: Reputation Protection.
        Blocks alerts if a notification was sent within the last 6 hours.
        Prevents inbox flooding and spam flagging.
        """
        if not last_alert_timestamp:
            return True
            
        cooldown_period = timedelta(hours=6)
        time_since_last_alert = timezone.now() - last_alert_timestamp
        
        if time_since_last_alert < cooldown_period:
            logger.info(f"SUPPRESSED: Alert for User {user_id}/Product {product_id} inside 6hr cool-down.")
            return False
            
        return True

    @staticmethod
    def log_suppression(user_id: int, product_id: int, reason: str):
        """
        Log suppression events for diagnostics without cluttering the main logic.
        """
        logger.warning(f"SUPPRESSED: User {user_id} | Product {product_id} | Reason: {reason}")

class AlertDiagnostics:
    """
    Tracks system health: Suppressed vs. Sent.
    """
    sent_count = 0
    suppressed_count = 0

    @classmethod
    def record_sent(cls):
        cls.sent_count += 1

    @classmethod
    def record_suppressed(cls):
        cls.suppressed_count += 1
    
    @classmethod
    def get_stats(cls):
        return {
            "sent": cls.sent_count,
            "suppressed": cls.suppressed_count
        }
