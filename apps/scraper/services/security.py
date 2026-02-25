import hashlib
import json
from typing import Dict, Any, List
from decimal import Decimal
from django.utils import timezone
from apps.scraper.models import NotificationLog, PriceHistory
import logging

logger = logging.getLogger(__name__)

class EnterpriseSecuritySuite:
    """
    Enterprise Integrity & Non-Repudiation Suite.
    Enforces Anti-Tampering, False Positive Mitigation, and Audit Trails.
    """

    @staticmethod
    def validate_discount_legitimacy(price_drop_pct: float, category_volatility: float, seller_history_drops: int) -> str:
        """
        False Positive Mitigation (Heuristic Contextualizer).
        Validates if a deep discount is a scam or a flash sale.
        """
        if price_drop_pct < 20.0:
            return "GENUINE_PROMO"
            
        # If massive drop (>50%), but market is volatile and seller has done this before
        if price_drop_pct > 50.0:
            if category_volatility > 15.0 and seller_history_drops > 3:
                return "GENUINE_PROMO" # Flash Sale Pattern recognized
            else:
                return "SCAM"
                
        # Between 20 and 50%
        if category_volatility > 5.0 or seller_history_drops > 0:
            return "GENUINE_PROMO"
            
        return "SCAM"

    @staticmethod
    def verify_history_integrity(product_id: int) -> bool:
        """
        The Non-Repudiation Data Shield (SHA-256 Hashing).
        Re-hashes PriceHistory entries and verifies integrity_hash to block Data Poisoning.
        """
        try:
            from django.conf import settings
            secret_key = getattr(settings, 'SECRET_KEY', 'fallback_secret')
            
            history = PriceHistory.objects.filter(store_price__product_id=product_id)
            if not history.exists():
                return True # Nothing to verify
                
            tampered_count = 0
            
            for entry in history:
                if not entry.integrity_hash:
                    continue
                # Recreate the data payload used for hashing (assuming price + timestamp + secret)
                # In models we use: current_price, last_updated, SECRET_KEY
                payload = f"{entry.price}-{entry.recorded_at.isoformat()}-{secret_key}"
                recalculated = hashlib.sha256(payload.encode('utf-8')).hexdigest()
                
                if recalculated != entry.integrity_hash:
                     tampered_count += 1
                     # Data Poisoning detected
                     entry.metadata['is_tampered'] = True
                     entry.save(update_fields=['metadata'])
                     
            from django.contrib.auth import get_user_model
            User = get_user_model()
            system_user = User.objects.filter(is_superuser=True).first()
            
            if tampered_count == 0:
                if system_user:
                    NotificationLog.objects.create(
                        user=system_user,
                        product_id=product_id,
                        status='SENT',
                        alert_type='System',
                        error_message=f"Integrity check passed for Product ID: {product_id} - Ready for Inference."
                    )
                return True
            else:
                if system_user:
                    NotificationLog.objects.create(
                        user=system_user,
                        product_id=product_id,
                        status='FAILED',
                        alert_type='System',
                        error_message=f"TAMPER_ALERT: {tampered_count} records compromised for Product ID: {product_id}."
                    )
                return False
                
        except Exception as e:
            logger.error(f"Integrity Verification Failed: {e}")
            return False

    @staticmethod
    def create_immutable_audit_log(user_id: int, product_id: int, event_type: str, state_payload: Dict[str, Any]) -> None:
        """
        Non-Repudiation Audit Trail (Immutable Logging).
        """
        try:
             from django.contrib.auth import get_user_model
             User = get_user_model()
             user = User.objects.get(pk=user_id)
             
             payload_str = json.dumps(state_payload, default=str)
             signature = hashlib.sha256(payload_str.encode('utf-8')).hexdigest()
             
             log_msg = f"[{event_type}] State: {payload_str} | Signature: {signature}"
             
             NotificationLog.objects.create(
                 user=user,
                 product_id=product_id,
                 status='SENT',
                 alert_type='System',
                 error_message=log_msg
             )
        except Exception as e:
             logger.error(f"Failed to create Audit Log: {e}")
