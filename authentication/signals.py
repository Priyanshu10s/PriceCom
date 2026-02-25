"""
apps/accounts/signals.py
Signal handlers for User model.
Currently disabled as Profile model is not yet defined in the new architecture.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger('authentication')
User = get_user_model()

# Note: Profile creation logic commented out until Profile model is restored.
# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         try:
#             # Profile.objects.create(user=instance)
#             logger.info(f"User created: {instance.email}")
#         except Exception as e:
#             logger.error(f"Error in user creation signal: {str(e)}")

# @receiver(post_save, sender=User)
# def save_user_profile(sender, instance, **kwargs):
#     pass
