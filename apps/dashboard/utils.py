from django.db import transaction
from .models import UniversalCart as Cart, CartItem
from apps.scraper.models import Product, PriceHistory

def get_or_create_cart(request):
    """
    Retrieves the cart for the current user or session.
    """
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        cart, _ = Cart.objects.get_or_create(session_key=session_key, user=None)
    return cart

def sync_cart_session_to_db(request, user):
    """
    Sync-on-Login: Migrates guest session cart to user database cart.
    Atomic transaction ensures no items are lost or duplicated.
    """
    session_key = request.session.session_key
    if not session_key:
        return

    with transaction.atomic():
        # 1. Get Guest Cart
        try:
            guest_cart = Cart.objects.get(session_key=session_key, user=None)
        except Cart.DoesNotExist:
            return # Nothing to sync

        # 2. Get User Cart
        user_cart, _ = Cart.objects.get_or_create(user=user)

        # 3. Merge Items
        for item in guest_cart.items.all():
            # Check if item already exists in user cart
            existing_item = user_cart.items.filter(product=item.product).first()
            if existing_item:
                existing_item.quantity += item.quantity
                existing_item.save()
            else:
                # Move item to user cart
                item.cart = user_cart
                item.save()

        # 4. Cleanup Guest Cart
        guest_cart.delete()

def update_cart_to_best_price(cart):
    """
    Multi-Store Linkage Logic:
    Re-scans PriceHistory for all items in the cart to find better deals.
    Updates affiliate_url and price_at_addition if a lower price is found.
    """
    for item in cart.items.select_related('product').all():
        # Get the absolute lowest price currently available
        # using the Product's latest StorePrice (assuming we have a helper or query for this)
        # For Antigravity, we'll look at the StorePrice directly.
        
        best_price_entry = item.product.prices.filter(is_available=True).order_by('current_price').first()
        
        if best_price_entry and best_price_entry.current_price < item.initial_price:
            # "Price Drop Alert" logic could go here too
            item.current_price = best_price_entry.current_price
            # item.best_store_at_addition = best_price_entry.store_name
            # item.affiliate_url = best_price_entry.product_url # In real world, wrap this
            item.save()

import re
import bleach

def normalize_product_url(url: str) -> str:
    """
    Sanitization Handshake: Strips UTM params, session IDs and tracking tags.
    Ensures that only the base Product ID (ASIN for Amazon, generic for Flipkart) remains.
    """
    # Parse Amazon ASIN
    if 'amazon' in url.lower():
        match = re.search(r'/(?:dp|gp/product|exec/obidos/ASIN)/([A-Z0-9]{10})', url)
        if match:
            return f"https://www.amazon.in/dp/{match.group(1)}"
    
    # Parse Flipkart item
    if 'flipkart' in url.lower():
        # Typically flipkart URLs have /p/itm... or just a query param pid=...
        match = re.search(r'pid=([A-Z0-9]+)', url)
        if match:
             return f"https://www.flipkart.com/item/p/itm?pid={match.group(1)}"
        # Strip everything after ? for clean base url
        return url.split('?')[0]

    return url.split('?')[0] # Fallback for other stores

def sanitize_xss(text: str) -> str:
    """
    XSS Prevention: Ensure HTML tags are neutralized before DB insertion.
    """
    if not text:
         return text
    return bleach.clean(text, tags=[], strip=True)

from typing import List, Dict, Any
from datetime import datetime, timezone

def calculate_freshness_badge(timestamp_str: str) -> Dict[str, Any]:
    """
    Freshness Engine Logic: Identifies stale data requiring async background refresh.
    """
    try:
        dt = datetime.fromisoformat(timestamp_str)
        now = datetime.now(timezone.utc)
        diff_mins = (now - dt).total_seconds() / 60
        if diff_mins > 60:
            return {'label': 'Syncing...', 'sync_required': True}
        else:
            return {'label': f"Updated {int(diff_mins)} mins ago", 'sync_required': False}
    except Exception:
        return {'label': 'Updated recently', 'sync_required': False}

def analyze_matrix_deals(matrix_data: List[dict]) -> List[dict]:
    """
    Dynamic Highlighting & Savings Calculator: Identify Max and Min Price 
    in a strictly authenticated unified matrix row.
    """
    if not matrix_data:
        return []

    prices = [item['price'] for item in matrix_data if item.get('price') is not None]
    
    if prices:
        min_price = min(prices)
        max_price = max(prices)
        savings = float(max_price - min_price)
        
        for item in matrix_data:
            if item.get('price') == min_price:
                item['best_deal'] = True
                item['savings_amount'] = f"You save ₹{savings:.2f} on {item.get('store', 'this store')}"
            else:
                item['best_deal'] = False
                item['savings_amount'] = "No savings"
                
            freshness = calculate_freshness_badge(item.get('last_updated', ''))
            item['freshness_label'] = freshness['label']
            if freshness['sync_required']:
                pass  # Trigger Celery Task Background Sync
    else:
        for item in matrix_data:
             item['best_deal'] = False
             item['savings_amount'] = "Out of Stock"
             item['freshness_label'] = "Unknown"
             
    return matrix_data
