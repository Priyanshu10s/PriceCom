from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
import hashlib
import hmac

from .models import PriceHistory

@receiver(post_save, sender=PriceHistory)
def automated_analytics(sender, instance, created, **kwargs):
    """
    The 'Force' Logic: Automated Signals
    Automatically calculates trends and cybersecurity hashes AFTER a save.
    
    Logic Flow:
    1. Check if this is a newly created record or a forced update.
    2. Fetch previous price history.
    3. Calculate percentage change & trend.
    4. Generate SHA-256 integrity hash.
    5. Save *again* (carefully preventing recursion loop is key here, but usage of 'update_fields' 
       or checking if hash exists can help, though standard practice is careful flag management. 
       However, since we just need to set these fields once, we can use `PriceHistory.objects.filter(pk=instance.pk).update(...)`
       to update without triggering signals again! This is the professional 'Topper Use' of signals).
    """
    
    # Only run logic if the hash is missing (implies new/unprocessed)
    # OR if we explicitly want to recalculate. 
    # For robust production, we check if integrity_hash is empty.
    
    if not instance.integrity_hash:
        try:
            # 1. Historical Context
            previous_entry = PriceHistory.objects.filter(
                store_price=instance.store_price,
                recorded_at__lt=instance.recorded_at
            ).exclude(pk=instance.pk).order_by('-recorded_at').first()

            # Default Values
            change_pct = Decimal('0.00')
            trend = 'STABLE'
            is_sig_drop = False

            # 2. Math Engine (Decimal Precision)
            if previous_entry and previous_entry.price and previous_entry.price > 0:
                current_price = Decimal(str(instance.price))
                prev_price = Decimal(str(previous_entry.price))
                
                # Formula: ((Current - Previous) / Previous) * 100
                raw_change = ((current_price - prev_price) / prev_price) * 100
                change_pct = raw_change.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                
                if change_pct < 0:
                    trend = 'DOWN'
                    if change_pct <= -10:
                        is_sig_drop = True
                elif change_pct > 0:
                    trend = 'UP'
            
            # 3. Cybersecurity (SHA-256 HMAC)
            # Integrity String: ID + Price + Timestamp
            secret = settings.SECRET_KEY.encode('utf-8')
            msg = f"{instance.id}-{instance.price}-{instance.recorded_at}".encode('utf-8')
            integrity_hash = hmac.new(secret, msg, hashlib.sha256).hexdigest()

            # 4. Atomic Update (Self-Performing Code)
            # Use .update() to avoid recursive signal loops (Zero-Recursion)
            PriceHistory.objects.filter(pk=instance.pk).update(
                change_percentage=change_pct,
                trend=trend,
                is_significant_drop=is_sig_drop,
                integrity_hash=integrity_hash,
                # Legacy fields removed in model, so we remove them here too.
            )
            
            # 5. Trigger Async Alert Check (Event-Driven Architecture)
            # "Fire and Forget" - Don't wait for email to send.
            from apps.scraper.tasks import check_alerts_task
            check_alerts_task.delay(instance.store_price.product.id)
            
        except Exception as e:
            # Log error silently or to a system logger
            print(f"Error in automated_analytics signal: {e}")
