import os
import django
import sys
import uuid
from django.db.models import Count

# Add project root to path
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.scraper.models import PriceAlert, Watchlist, Product

def fix_duplicates(model):
    print(f"Checking {model.__name__}...")
    duplicates = model.objects.values('uuid').annotate(count=Count('uuid')).filter(count__gt=1)
    
    count = 0
    for dep in duplicates:
        u_val = dep['uuid']
        # Get all objects with this UUID
        objs = model.objects.filter(uuid=u_val)
        # Update all but the first one? Or all of them to be safe?
        # Update ALL of them to new UUIDs just to be safe and random.
        for obj in objs:
            obj.uuid = uuid.uuid4()
            obj.save()
            count += 1
            
    # Also check for NULLs just in case
    nulls = model.objects.filter(uuid__isnull=True)
    for obj in nulls:
        obj.uuid = uuid.uuid4()
        obj.save()
        count += 1
        
    print(f"Fixed {count} records in {model.__name__}")

if __name__ == "__main__":
    fix_duplicates(PriceAlert)
    fix_duplicates(Watchlist)
    fix_duplicates(Product)
