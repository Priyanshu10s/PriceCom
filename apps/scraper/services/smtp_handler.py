import logging
import traceback
from django.core.mail import send_mail
from django.db import transaction
from django.conf import settings
from apps.scraper.models import NotificationLog, Product

logger = logging.getLogger('apps.scraper')

def send_monitored_email(user, subject: str, message: str, product: Product = None, current_price=None, alert_type='Drop'):
    """
    The 'Intent-Result' Handshake Logic.
    Tracks every email intent and its final server response based on Non-Repudiation.
    """
    # Step 1 (Intent): Create/Start Log Pending
    # Atomic Transaction: Log is created even if email hangs/fails strictly speaking? 
    # Actually, we want log created BEFORE we try sending.
    # transaction.atomic ensures data integrity.
    
    log_entry = None
    
    try:
        with transaction.atomic():
            log_entry = NotificationLog.objects.create(
                user=user,
                product=product,
                price_at_alert=current_price,
                status='PENDING',
                alert_type=alert_type
            )

        # Step 2 (The Try-Except Block): Execute Command
        try:
            # Simulated SMTP Send
            sent_count = send_mail(
                subject=subject,
                message=message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
                fail_silently=False, # We want exceptions!
            )
            
            if sent_count > 0:
                # Step 3 (Result): Success
                log_entry.status = 'SENT'
                log_entry.smtp_response_code = "250 OK" # Standard Success
                log_entry.save()
                return True
            else:
                # Weird case where no exception but 0 sent
                log_entry.status = 'FAILED'
                log_entry.error_message = "SMTP returned 0 sent count."
                log_entry.save()
                return False

        except Exception as e:
            # The Fail-Safe
            error_trace = traceback.format_exc()
            log_entry.status = 'FAILED'
            log_entry.save(update_fields=['status']) # Force Save Status First
            log_entry.log_event(error_trace) # Truncates if needed
            logger.error(f"SMTP FAILED: {e}")
            return False
            
    except Exception as e:
        # DB Error creating log?
        logger.critical(f"CRITICAL: Failed to create Audit Log! {e}")
        return False
