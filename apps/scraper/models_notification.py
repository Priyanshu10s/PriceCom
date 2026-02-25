
class NotificationLog(models.Model):
    """
    High-Trust Audit Trail System.
    Tracks every email intent and its final server response based on Non-Repudiation.
    """
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
    
    import uuid
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, help_text="Traceability ID")
    
    # Relational Integrity
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notification_logs')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='notification_logs', null=True, blank=True)
    
    # Snapshot Data ("State-of-the-World")
    price_at_alert = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Price at the exact moment of alert")
    
    # Status Engine
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING', db_index=True)
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPE_CHOICES, default='Drop')
    
    # Audit Fields
    intent_timestamp = models.DateTimeField(auto_now_add=True, help_text="Exact millisecond system decided to alert")
    smtp_response_code = models.CharField(max_length=10, null=True, blank=True, help_text="e.g. 250 OK, 550 Rejected")
    error_message = models.TextField(null=True, blank=True, help_text="Raw SMTP traceback")
    
    class Meta:
        ordering = ['-intent_timestamp']
        verbose_name = "Notification Log"
        verbose_name_plural = "Audit Trail"

    def log_event(self, message: str):
        """
        Automatically truncates long error messages to prevent database bloat.
        Keeps the "Audit Trail" clean.
        """
        MAX_LEN = 2000
        if message and len(message) > MAX_LEN:
            self.error_message = message[:MAX_LEN] + "... [TRUNCATED]"
        else:
            self.error_message = message
        self.save(update_fields=['error_message'])

    @property
    def is_delivered(self) -> bool:
        """Professional Debugging Tool: Quick Boolean check."""
        return self.status == 'SENT'

    def __str__(self):
        return f"{self.get_status_display()} - {self.user} - {self.intent_timestamp}"
