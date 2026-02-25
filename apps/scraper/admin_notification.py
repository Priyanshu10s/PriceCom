
from .models import NotificationLog

@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    """
    The 'Topper' Admin Interface.
    High-Precision Auditing Tool.
    """
    list_display = ('current_status_badge', 'price_at_alert', 'user', 'intent_timestamp', 'alert_type')
    list_filter = ('status', 'created_at', 'alert_type')
    search_fields = ('user__email', 'product__name', 'uuid')
    readonly_fields = ('intent_timestamp', 'error_message', 'uuid', 'smtp_response_code')
    
    fieldsets = (
        ('Traceability', {
            'fields': ('uuid', 'intent_timestamp')
        }),
        ('Context', {
            'fields': ('user', 'product', 'price_at_alert', 'alert_type')
        }),
        ('Audit Outcome', {
            'fields': ('status', 'smtp_response_code', 'error_message')
        }),
    )

    def current_status_badge(self, obj):
        # Visual Aid (Simulated text decoration)
        return f"{obj.status.upper()}"
    current_status_badge.short_description = 'Status'
