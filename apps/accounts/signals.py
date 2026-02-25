"""
apps/accounts/signals.py
Signal handlers for User model.
Currently disabled as Profile model is not yet defined in the new architecture.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger('apps.accounts')
User = get_user_model()

# [FORCE LOGIC] Dependency Injection: Import required cross-app models
from apps.accounts.models import Wallet
from apps.scraper.models import Watchlist

@receiver(post_save, sender=User)
def initialize_user_ecosystem(sender, instance, created, **kwargs) -> None:
    """
    [FORCE LOGIC] Atomic State Transition: Automatically wires a
    Wallet and an empty Watchlist to every newly registered user.
    """
    if created:
        try:
            Wallet.objects.get_or_create(user=instance)
            Watchlist.objects.get_or_create(user=instance)
            logger.info(f"System Alignment Success: Initialized Wallet & Watchlist for {instance.email}")
        except Exception as e:
            logger.error(f"Ecosystem Initialization Failed for {instance.email}: {str(e)}")
