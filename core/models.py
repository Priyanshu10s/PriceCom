from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    brand = models.CharField(max_length=100, null=True, blank=True)
    category = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.name

class StorePrice(models.Model):
    STORE_CHOICES = [
        ('Amazon', 'Amazon'),
        ('Flipkart', 'Flipkart'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='prices')
    store_name = models.CharField(max_length=50, choices=STORE_CHOICES)
    current_price = models.DecimalField(max_digits=10, decimal_places=2)
    product_url = models.URLField(max_length=500)
    image_url = models.URLField(max_length=500, null=True, blank=True)
    is_available = models.BooleanField(default=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('product', 'store_name')

    def __str__(self):
        return f"{self.product.name} - {self.store_name} - {self.current_price}"

class PriceHistory(models.Model):
    store_price = models.ForeignKey(StorePrice, on_delete=models.CASCADE, related_name='history')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-recorded_at']

    def __str__(self):
        return f"{self.store_price} - {self.price} @ {self.recorded_at}"
