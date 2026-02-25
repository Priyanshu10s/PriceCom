from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .utils import sync_cart_session_to_db

@receiver(user_logged_in)
def handle_user_login(sender, user, request, **kwargs):
    """
    Trigger the Cart Sync automatically when a user logs in.
    Ensures seamless transition from Mobile Guest -> Desktop User.
    """
    if request:
        sync_cart_session_to_db(request, user)
