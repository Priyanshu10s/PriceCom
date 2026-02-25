from django.contrib import admin
from .models import Product, StorePrice, PriceHistory, Category, NotificationLog

class StorePriceInline(admin.TabularInline):
    model = StorePrice
    extra = 1

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'icon')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand_name', 'category', 'current_lowest_price', 'is_active')
    search_fields = ('name', 'brand_name', 'sku')
    list_filter = ('category', 'is_active', 'is_featured')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [StorePriceInline]

@admin.register(StorePrice)
class StorePriceAdmin(admin.ModelAdmin):
    list_display = ('product', 'store_name', 'current_price', 'is_available', 'last_updated')
    list_filter = ('store_name', 'is_available', 'last_updated')
    search_fields = ('product__name', 'product_url')

@admin.register(PriceHistory)
class PriceHistoryAdmin(admin.ModelAdmin):
    list_display = ('store_price', 'price', 'recorded_at')
    readonly_fields = ('recorded_at',)
    list_filter = ('recorded_at',)

@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    """
    The 'Topper' Admin Interface.
    High-Precision Auditing Tool.
    """
    list_display = ('current_status_badge', 'price_at_alert', 'user', 'intent_timestamp', 'alert_type')
    list_filter = ('status', 'intent_timestamp', 'alert_type')
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