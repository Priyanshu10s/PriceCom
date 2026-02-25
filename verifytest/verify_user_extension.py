import os
import django
import sys

# Add project root to path
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.scraper.models import PriceAlert

User = get_user_model()

def run_verification():
    print("--- User Model Extension Verification ---")
    
    # 1. Test User Fields
    user = User.objects.first()
    if not user:
        print("No users found. Creating test user...")
        user = User.objects.create_user(username='testuser_ext', email='test_ext@example.com', password='password123')
    
    print(f"Testing on User: {user.email}")
    
    # Check default
    print(f"   Default Alert Frequency: {user.alert_frequency}")
    if user.alert_frequency == 'DAILY_DIGEST':
        print("   [OK] Default Frequency is DAILY_DIGEST")
    else:
        print(f"   [FAIL] Default Frequency is {user.alert_frequency}")
        
    # Change Frequency
    user.alert_frequency = 'INSTANT'
    user.save()
    user.refresh_from_db()
    print(f"   Updated Alert Frequency: {user.alert_frequency}")
    
    if user.alert_frequency == 'INSTANT':
        print("   [OK] Frequency update successful")
    else:
        print("   [FAIL] Frequency update failed")
        
    # 2. Test get_pending_alerts
    # Create dummy alerts
    PriceAlert.objects.filter(user=user).delete()
    PriceAlert.objects.create(user=user, product_url='http://test.com/1', target_price=100)
    PriceAlert.objects.create(user=user, product_url='http://test.com/2', target_price=200, is_triggered=True)
    
    pending_alerts = user.get_pending_alerts()
    count = pending_alerts.count()
    print(f"   Pending Alerts (Expected 1): {count}")
    
    if count == 1:
        print("   [OK] get_pending_alerts() filtering correctly")
    else:
        print(f"   [FAIL] get_pending_alerts() failed. Count: {count}")
        
    print("\n--- End Verification ---")

if __name__ == "__main__":
    run_verification()
