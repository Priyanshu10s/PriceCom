import uuid
from django.db import models
from django.conf import settings
from apps.scraper.models import Product

class UniversalCart(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='universal_cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
         return f"Cart for {self.user.email}"

class CartItem(models.Model):
    STORE_CHOICES = [
        ('Amazon', 'Amazon'),
        ('Flipkart', 'Flipkart'),
    ]
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    cart = models.ForeignKey(UniversalCart, on_delete=models.CASCADE, related_name='items')
    product_url = models.URLField(max_length=2000)
    store_name = models.CharField(max_length=50, choices=STORE_CHOICES)
    initial_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    current_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    last_synced = models.DateTimeField(null=True, blank=True)
    is_stock_available = models.BooleanField(default=True)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
         return f"{self.store_name} Item in {self.cart}"

class PriceHistoryLog(models.Model):
    cart_item = models.ForeignKey(CartItem, on_delete=models.CASCADE, related_name='price_history')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
         ordering = ['-recorded_at']

class RedirectionLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    store_name = models.CharField(max_length=50)
    target_url = models.URLField(max_length=2000)
    price_at_click = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user or getattr(self, 'session_key', 'Anon')} -> {self.store_name}"
