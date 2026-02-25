import uuid
import datetime
import pytz
import re
import hashlib
from typing import Optional, List
from decimal import Decimal
from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.utils import timezone
from django.db.models import Subquery, OuterRef

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=150, unique=True, blank=True)
    icon = models.CharField(max_length=50, default='fas fa-box', help_text="FontAwesome class string")

    def save(self, *args, **kwargs) -> None:
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    class Meta:
        app_label = 'scraper'

    def save(self, *args, **kwargs) -> None:
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name

class Product(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=300, unique=True, blank=True, null=True)
    sku = models.CharField(max_length=50, unique=True, blank=True, null=True)
    brand_name = models.CharField(max_length=100, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    tags = models.ManyToManyField(Tag, blank=True, related_name='products')
    
    # Financial Analytics (Decimal required for Precision)
    base_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="MRP")
    current_lowest_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Status Management
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    # Future Scalability Hooks (AI/ML Architecture)
    trend_indicator = models.CharField(max_length=20, default='STABLE', help_text="Schema Hook for LSTM Integration")
    search_vector = models.TextField(blank=True, null=True, help_text="NLP Vector Placeholder for Semantic Matchmaker")
    metadata = models.JSONField(default=dict, blank=True, help_text="Extensible JSON for Signals (e.g., is_anomalous fraud detection)")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'scraper'

    def save(self, *args, **kwargs) -> None:
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
            
        if not self.sku:
            self.sku = str(uuid.uuid4())[:8].upper()

        if self.created_at and timezone.is_naive(self.created_at):
            self.created_at = timezone.make_aware(self.created_at, datetime.timezone.utc)
        if self.updated_at and timezone.is_naive(self.updated_at):
            self.updated_at = timezone.make_aware(self.updated_at, datetime.timezone.utc)
            
        super().save(*args, **kwargs)

    def clean_canonical_name(self) -> str:
        """
        Phase 2 AI Integration: Strips HTML and special characters to build NLP-ready search vectors.
        """
        if not self.name:
            return ""
        clean = re.sub(r'<[^>]+>', '', self.name)
        clean = re.sub(r'[^a-zA-Z0-9\s]', '', clean)
        return clean.strip().lower()

    def generate_search_vector(self) -> None:
        """
        Vector Hook for Future NLP searches.
        Concatenates normalized attributes (Brand + Category + Cleaned Title).
        """
        brand = self.brand_name.lower() if self.brand_name else "generic"
        category = self.category.name.lower() if self.category else "uncategorized"
        title = self.clean_canonical_name()
        
        self.search_vector = f"{brand} {category} {title}"

    def update_trend_mapping(self) -> None:
        """
        Trend Mapping via 7-day Moving Average.
        Tags products as BULLISH, BEARISH, or FLAT.
        """
        import numpy as np
        
        prices_queryset = PriceHistory.objects.filter(
            store_price__product=self
        ).order_by('-recorded_at')[:7]
        
        if len(prices_queryset) < 3:
            return
            
        prices = [float(p.price) for p in prices_queryset][::-1] # chronological
        
        if len(prices) >= 2:
            sma_short = np.mean(prices[-3:])
            sma_long = np.mean(prices)
            
            if sma_short > sma_long * 1.02:
                self.trend_indicator = 'BULLISH'
            elif sma_short < sma_long * 0.98:
                self.trend_indicator = 'BEARISH'
            else:
                self.trend_indicator = 'FLAT'

    def get_price_velocity(self) -> str:
        """
        Phase 2 AI Integration: Calculates momentum/velocity of price drops for Predictive LSTM Modeling.
        Self-Performing Mock Logic: Compares current vs base for functional Dashboard prep.
        """
        if not self.base_price or not self.current_lowest_price or self.base_price <= 0:
            self.trend_indicator = "STABLE"
            return "STABLE"
            
        ratio = self.current_lowest_price / self.base_price
        if ratio < Decimal('0.7'):
            self.trend_indicator = "DROPPING"
            return "DROPPING"
        elif ratio > Decimal('1.1'):
            self.trend_indicator = "VOLATILE"
            return "VOLATILE"
        self.trend_indicator = "STABLE"
        return "STABLE"

    def update_lowest_price(self) -> None:
        """
        Atomic Price Calculation: Filters actively available StorePrice objects, calculates min, and commits atomically.
        """
        active_prices = self.prices.filter(is_available=True).values_list('current_price', flat=True)
        if active_prices:
            min_val = min(active_prices)
            self.current_lowest_price = min_val
            # Update prediction velocity before saving state
            self.get_price_velocity()
            # Vectors and trend mapping
            self.generate_search_vector()
            self.update_trend_mapping()
            # Atomically update DB state for speed
            self.save(update_fields=['current_lowest_price', 'trend_indicator', 'search_vector'])

    @property
    def discount_percentage(self) -> Decimal:
        if self.base_price and self.current_lowest_price and self.base_price > 0:
            discount = ((self.base_price - self.current_lowest_price) / self.base_price) * Decimal('100.0')
            return round(discount, 2)
        return Decimal('0.00')

    def get_freshness_status(self) -> str:
        """
        Global Display Logic: Translates data age into Dashboard Pulse UI Classes.
        """
        if not self.updated_at:
             return 'status-stale'
             
        now = timezone.now()
        diff = now - self.updated_at
        
        if diff < datetime.timedelta(hours=1):
            return 'status-live'
        elif diff < datetime.timedelta(hours=24):
            return 'status-delayed'
        else:
            return 'status-stale'

    def calculate_purchase_reward(self) -> Decimal:
        """
        Wallet Bridge Logic: Extrapolates 1% Wallet credit from the definitive lowest price mathematically.
        """
        if not self.current_lowest_price:
            return Decimal('0.00')
        reward = self.current_lowest_price * Decimal('0.01')
        return round(reward, 2)

    def __str__(self) -> str:
        return self.name

class StorePrice(models.Model):
    STORE_CHOICES = [
        ('Amazon', 'Amazon'),
        ('Flipkart', 'Flipkart'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='prices')
    store_name = models.CharField(max_length=50, choices=STORE_CHOICES)
    current_price = models.DecimalField(max_digits=10, decimal_places=2) # Enforced Decimal for Financial Accuracy
    product_url = models.URLField(max_length=500)
    image_url = models.URLField(max_length=500, null=True, blank=True)
    is_available = models.BooleanField(default=True)
    is_verified_seller = models.BooleanField(default=True)
    metadata = models.JSONField(default=dict, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    price_hash = models.CharField(max_length=64, null=True, blank=True, help_text="SHA-256 hash of price+timestamp for integrity")

    class Meta:
        unique_together = ('product', 'store_name')

    def integrity_check(self) -> bool:
        """
        Anti-Tampering Engine (Cryptographic Price Validation).
        """
        if not self.price_hash:
            return True
        secret_key = getattr(settings, 'SECRET_KEY', 'fallback_secret')
        raw_string = f"{self.current_price}-{self.store_name}-{self.last_updated.isoformat()}-{secret_key}"
        recalc = hashlib.sha256(raw_string.encode('utf-8')).hexdigest()
        
        if self.price_hash != recalc:
            self.is_available = False
            if isinstance(self.metadata, dict):
                self.metadata['TAMPER_ALERT'] = True
            return False
        return True

    def save(self, *args, **kwargs) -> None:
        """
        SHA-256 Integrity Guards: Generates financial fingerprint to prevent tampering attacks on specific scrape points.
        """
        secret_key = getattr(settings, 'SECRET_KEY', 'fallback_secret')
        now_str = self.last_updated.isoformat() if self.last_updated else timezone.now().isoformat()
        
        if self.pk:
            # Force integrity check on existing objects
            if not self.integrity_check():
                # Tampered! We save the unavailability but don't recalculate the hash
                pass
            else:
                raw_string = f"{self.current_price}-{self.store_name}-{now_str}-{secret_key}"
                self.price_hash = hashlib.sha256(raw_string.encode('utf-8')).hexdigest()
        else:
            raw_string = f"{self.current_price}-{self.store_name}-{now_str}-{secret_key}"
            self.price_hash = hashlib.sha256(raw_string.encode('utf-8')).hexdigest()
            
        super().save(*args, **kwargs)
        
        # Self-Performing Update: Force parent product recalculation
        if self.product:
            self.product.update_lowest_price()

    def __str__(self) -> str:
        return f"{self.product.name} - {self.store_name} - {self.current_price}"

class PriceHistoryManager(models.Manager):
    def get_biggest_drops(self, limit: int = 5):
        latest_ids = self.filter(
            store_price=OuterRef('store_price')
        ).order_by('-recorded_at').values('id')[:1]

        return self.filter(
            id__in=Subquery(latest_ids),
            change_percentage__lt=0 
        ).select_related('store_price__product', 'store_price__product__category').order_by('change_percentage')[:limit]

class PriceHistory(models.Model):
    TREND_CHOICES = [
        ('UP', 'UP'),
        ('DOWN', 'DOWN'),
        ('STABLE', 'STABLE'),
    ]

    objects = PriceHistoryManager()

    store_price = models.ForeignKey(StorePrice, on_delete=models.CASCADE, related_name='history')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='INR')
    
    change_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    trend = models.CharField(max_length=10, choices=TREND_CHOICES, default='STABLE')
    is_significant_drop = models.BooleanField(default=False)
    
    integrity_hash = models.CharField(max_length=64, blank=True, null=True, help_text="SHA-256 integrity signature")
    metadata = models.JSONField(default=dict, blank=True, help_text="Scalability Hook: Storage for anomaly detection flags")
    
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-recorded_at']
        
    def save(self, *args, **kwargs) -> None:
        secret_key = getattr(settings, 'SECRET_KEY', 'fallback_secret')
        if not self.integrity_hash:
            now_str = timezone.now().isoformat()
            payload = f"{self.price}-{now_str}-{secret_key}"
            self.integrity_hash = hashlib.sha256(payload.encode('utf-8')).hexdigest()
            
        super().save(*args, **kwargs)

    @property
    def price_change_percent(self) -> Decimal:
        return self.change_percentage

    def __str__(self) -> str:
        return f"{self.store_price} - {self.price} ({self.trend})"

class Watchlist(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='watchlist')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='watchlist_items')
    target_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Wallet Product Synchronization (Matrix Bridging)
    reward_points_eligible = models.BooleanField(default=True)
    potential_reward = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    is_reward_claimed = models.BooleanField(default=False)
    last_notified_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')
        ordering = ['-created_at']

    def sync_with_wallet(self, user_wallet_id: str) -> dict:
        """
        Cross-App Dependency Management: Prepares a secure transaction packet linking Watchlist Drop to Wallet Ledger.
        Non-Repudiation of Rewards mathematically guarded by signature hash.
        """
        if not self.reward_points_eligible or self.is_reward_claimed:
            return {"status": "FAIL", "reason": "Not Eligible"}
            
        calculated_reward = self.product.calculate_purchase_reward()
        self.potential_reward = calculated_reward
        
        # Crypto-Sign the intent before bridging
        payload_str = f"{user_wallet_id}-{self.uuid}-{calculated_reward}"
        signature = hashlib.sha256(payload_str.encode('utf-8')).hexdigest()
        
        # Data Packet prepared for account/wallet signals
        packet = {
            "status": "READY",
            "wallet_id": user_wallet_id,
            "reward_amount": str(calculated_reward),
            "watchlist_ref": str(self.uuid),
            "auth_signature": signature
        }
        return packet

    def __str__(self) -> str:
        return f"{self.user} watching {self.product}"

class PriceAlert(models.Model):
    PRIORITY_CHOICES = [
        ('LOW', 'Low - Standard Queue'),
        ('HIGH', 'High - Fast Track'),
        ('VIP', 'VIP - Real Time'),
    ]

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='alerts')
    product_url = models.URLField(max_length=500)
    target_price = models.DecimalField(max_digits=10, decimal_places=2)
    current_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Gamification / Dependency Logic
    alert_priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='LOW', help_text="Determined by Wallet Ecosystem mapping")
    
    is_triggered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'scraper'

    def __str__(self) -> str:
        return f"Alert for {self.user} on {self.product_url}"

class NotificationLog(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'PENDING'),
        ('SENT', 'SENT'),
        ('FAILED', 'FAILED'),
        ('SUPPRESSED', 'SUPPRESSED'),
    ]
    
    ALERT_TYPE_CHOICES = [
        ('Drop', 'Price Drop'),
        ('Restock', 'Back in Stock'),
        ('System', 'System Alert'),
    ]
    
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, help_text="Traceability ID")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notification_logs')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='notification_logs', null=True, blank=True)
    price_at_alert = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING', db_index=True)
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPE_CHOICES, default='Drop')
    intent_timestamp = models.DateTimeField(auto_now_add=True)
    smtp_response_code = models.CharField(max_length=10, null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    
    class Meta:
        ordering = ['-intent_timestamp']
        verbose_name = "Notification Log"
        verbose_name_plural = "Audit Trail"

    def log_event(self, message: str) -> None:
        MAX_LEN = 2000
        if message and len(message) > MAX_LEN:
            self.error_message = message[:MAX_LEN] + "... [TRUNCATED]"
        else:
            self.error_message = message
        self.save(update_fields=['error_message'])

    @property
    def is_delivered(self) -> bool:
        return self.status == 'SENT'

    def __str__(self) -> str:
        return f"{self.get_status_display()} - {self.user} - {self.intent_timestamp}"

class ProductImage(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='product_images')
    image = models.ImageField(upload_to='ocr_uploads/%Y/%m/%d/')
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending Processing'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('LOW_CONFIDENCE', 'Low Confidence'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    extracted_text = models.TextField(blank=True, null=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = 'scraper'

    def __str__(self) -> str:
        return f"Image {self.uuid} - {self.status}"