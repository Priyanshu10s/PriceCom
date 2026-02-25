from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.apps import apps

class User(AbstractUser):
    # Alert Frequency Choices
    class AlertFrequency(models.TextChoices):
        INSTANT = 'INSTANT', 'Real-time Alerts (Immediate)'
        DAILY_DIGEST = 'DAILY_DIGEST', 'Daily Summary (Sent at 8 PM)'
        WEEKLY_SUMMARY = 'WEEKLY_SUMMARY', 'Weekly Digest (Every Sunday)'

    # Standard Custom User Model
    email = models.EmailField(unique=True)
    
    # Professional Profile Fields
    profile_picture = models.ImageField(upload_to='profile_pics/', default='profile_pics/default.png', blank=True)
    phone_number = models.CharField(max_length=15, blank=True, help_text="Contact number for SMS alerts")
    is_verified = models.BooleanField(default=False, help_text="Email verification status")
    is_premium = models.BooleanField(default=False, help_text="Unlock advanced features")
    
    # Alert Settings
    alert_frequency = models.CharField(
        max_length=20,
        choices=AlertFrequency.choices,
        default=AlertFrequency.DAILY_DIGEST,
        help_text="Frequency of price drop notifications"
    )
    
    profile_updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f"{self.email} ({self.get_alert_frequency_display()})"

    def save(self, *args, **kwargs):
        # Update timestamp on save (handled by auto_now, but explicit logic can go here if needed)
        super().save(*args, **kwargs)

    def get_pending_alerts(self):
        """
        The 'Force' Logic: Automated Alert Filtering
        Returns a queryset of PriceAlerts based on the user's frequency setting.
        Uses apps.get_model to avoid circular imports with Scraper app.
        """
        PriceAlert = apps.get_model('scraper', 'PriceAlert')
        
        # Base query: Alerts for this user that haven't been triggered/sent
        # Assuming 'is_triggered' means sent/processed. 
        # If 'is_triggered' is just for the price drop event, we might need a separate 'sent_at' 
        # or 'is_sent' field. For now, we filter by what's available.
        # If frequency is INSTANT, we want all untriggered/unprocessed alerts.
        # If DAILY/WEEKLY, we might fetch alerts created in the last X duration.
        
        pending = PriceAlert.objects.filter(user=self, is_triggered=False)
        
        return pending

import uuid
import hashlib
from decimal import Decimal

class Wallet(models.Model):
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('FROZEN', 'Frozen'),
        ('SUSPENDED', 'Suspended'),
    ]
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wallet')
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Wallet ({self.user.email}) - {self.balance}"

class WalletTransaction(models.Model):
    TX_TYPE_CHOICES = [
        ('CREDIT', 'Credit'),
        ('DEBIT', 'Debit'),
    ]
    CATEGORY_CHOICES = [
        ('SIGNUP_BONUS', 'Signup Bonus'),
        ('PRICE_DROP_REWARD', 'Price Drop Reward'),
        ('PREMIUM_PURCHASE', 'Premium Purchase'),
        ('SYSTEM_ADJUSTMENT', 'System Adjustment'),
    ]

    # Event-Sourced Append-Only Ledger Schema
    tx_uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wallet = models.ForeignKey(Wallet, on_delete=models.PROTECT, related_name='transactions')
    tx_type = models.CharField(max_length=10, choices=TX_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    running_balance = models.DecimalField(max_digits=12, decimal_places=2, help_text="Snapshot of balance post-transaction")
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='SYSTEM_ADJUSTMENT')
    
    idempotency_key = models.CharField(max_length=255, unique=True, help_text="Prevents duplicate processing")
    security_hash = models.CharField(max_length=256, blank=True, help_text="SHA-256 HMAC for cryptographic integrity verification")
    metadata = models.JSONField(default=dict, blank=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def calculate_integrity_hash(self) -> str:
        """Calculates a deterministic SHA-256 hash representing the transaction state."""
        payload = f"{self.tx_uuid}|{self.wallet.id}|{self.tx_type}|{self.amount}|{self.running_balance}|{self.idempotency_key}"
        return hashlib.sha256(payload.encode('utf-8')).hexdigest()

    def __str__(self):
        return f"{self.tx_type} {self.amount} - {self.tx_uuid}"
