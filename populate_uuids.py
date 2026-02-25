import os
import django
import sys
import uuid

# Add project root to path
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.scraper.models import Product, Watchlist, PriceAlert

def populate_uuids():
    print("--- Populating UUIDs ---")
    
    # Product
    products = Product.objects.filter(uuid__isnull=True)
    print(f"Products to update: {products.count()}")
    for p in products:
        p.uuid = uuid.uuid4()
        p.save()
        
    # Watchlist
    watchlists = Watchlist.objects.filter(uuid__isnull=True)
    print(f"Watchlists to update: {watchlists.count()}")
    for w in watchlists:
        w.uuid = uuid.uuid4()
        w.save()

    # PriceAlert
    alerts = PriceAlert.objects.filter(uuid__isnull=True)
    print(f"PriceAlerts to update: {alerts.count()}")
    for a in alerts:
        a.uuid = uuid.uuid4()
        a.save()
        
    print("--- Done ---")

if __name__ == "__main__":
    populate_uuids()
