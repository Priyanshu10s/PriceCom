from django.contrib import admin
from .models import Product, StorePrice, PriceHistory

class StorePriceInline(admin.TabularInline):
    model = StorePrice
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'category')
    search_fields = ('name', 'brand')
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
