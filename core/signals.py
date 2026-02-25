from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import StorePrice, PriceHistory

@receiver(post_save, sender=StorePrice)
def create_price_history(sender, instance, created, **kwargs):
    """
    Automatically creates a PriceHistory entry when a StorePrice is saved.
    Ensures history is recorded only when the price actually changes or on creation.
    """
    # Check the latest history entry to avoid duplicates if price hasn't changed.
    last_history = instance.history.first()
    
    if created or not last_history or last_history.price != instance.current_price:
        PriceHistory.objects.create(
            store_price=instance,
            price=instance.current_price
        )
