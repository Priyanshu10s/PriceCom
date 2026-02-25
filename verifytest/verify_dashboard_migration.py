import os
import django
import sys

# Add project root to path
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.scraper.models import Product, Category

print("--- Verification Report ---")
product_count = Product.objects.count()
category_count = Category.objects.count()
print(f"Total Products: {product_count}")
print(f"Total Categories: {category_count}")

if product_count > 0:
    p = Product.objects.first()
    print(f"\nSample Product:\n Name: {p.name}\n Slug: {p.slug}\n SKU: {p.sku}\n Category: {p.category}\n Brand: {p.brand_name}\n Created: {p.created_at}")
else:
    print("No products found to verify.")

print("\n--- End Report ---")
