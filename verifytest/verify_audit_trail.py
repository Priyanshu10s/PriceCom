import os
import django
import sys
from django.conf import settings

# Add project root to path
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.accounts.models import User
from apps.scraper.models import Product, NotificationLog, Category
from apps.scraper.services.smtp_handler import send_monitored_email
from apps.scraper.services.metrics import AlertMetricsManager

def run_audit_verification():
    print("--- High-Trust Audit Trail Verification ---")
    
    # Setup Data
    u, _ = User.objects.get_or_create(email='audit_test@example.com', username='audit_test')
    c, _ = Category.objects.get_or_create(name='AuditCat')
    p = Product.objects.create(name="Audit Widget", category=c, current_lowest_price=99.99)
    
    # 1. Test "Intent-Result" Handshake (Simulated Failure)
    # We expect this to fail because EMAIL_HOST might not be configured real, or we simulate it.
    # Actually, verify_smtp_handler logic should create a log regardless.
    print("\n1. [SMTP Handshake Test]")
    try:
        # This might actually try to send email. If it fails (connection refused), we check if LOG is FAILED.
        success = send_monitored_email(u, "Test Subject", "Test Body", p, 99.99)
        print(f"   Email Sent Result: {success}")
    except Exception as e:
        print(f"   Exception during send: {e}")
        
    # Check Log
    log = NotificationLog.objects.filter(user=u).last()
    if log:
        print(f"   Log Created: {log.status} | Trace: {log.uuid}")
        if log.status in ['SENT', 'FAILED']:
            print("   [OK] Logged final status correctly")
            if log.status == 'FAILED':
                 print(f"   [OK] Error Captured: {log.error_message[:50]}...")
        else:
             print(f"   [FAIL] Log stuck in {log.status}")
    else:
        print("   [FAIL] No Log Created!")

    # 2. Test Metrics Engine
    print("\n2. [Metrics Engine Report]")
    report = AlertMetricsManager.generate_30_day_report()
    print(f"   Total Alerts: {report['total_alerts']}")
    if report['total_alerts'] >= 1:
        print("   [OK] Metrics capturing data")
    else:
        print("   [FAIL] Metrics empty")

    # Cleanup
    NotificationLog.objects.filter(user=u).delete()
    p.delete()
    c.delete()
    u.delete()
    print("\n--- Verified ---")

if __name__ == "__main__":
    run_audit_verification()
