from typing import Dict, Any, List
from .models import CartItem

class TeamHandshakeSerializer:
    """
    High-Performance Data Mapper.
    Extracts backend CartItem models into frontend-friendly JSON dictionaries.
    "Plug-and-Play" design for the UI developer.
    """
    
    @staticmethod
    def get_store_logo(store_name: str) -> str:
        if store_name.lower() == 'amazon':
            return '/static/images/amazon_logo.png'
        elif store_name.lower() == 'flipkart':
            return '/static/images/flipkart_logo.png'
        return '/static/images/default_store.png'

    @staticmethod
    def serialize_item(item: CartItem) -> Dict[str, Any]:
        """
        Serializes a single CartItem.
        Pre-calculates price_diff for instant UI rendering.
        """
        initial = item.initial_price or 0
        current = item.current_price or 0
        price_diff = int(initial - current)
        
        # Determine confidence score (Mock logic for now, could be derived from scraper metadata)
        confidence_score = 98 if item.last_synced else 50
        
        return {
            'item_uuid': str(item.uuid),
            'product_url': item.product_url,
            'store_name': item.store_name,
            'initial_price': float(initial),
            'current_price': float(current),
            'price_diff': price_diff,
            'store_logo_url': TeamHandshakeSerializer.get_store_logo(item.store_name),
            'confidence_score': confidence_score,
            'is_stock_available': item.is_stock_available,
            'last_synced': item.last_synced.isoformat() if item.last_synced else None
        }

    @staticmethod
    def serialize_queryset(queryset) -> List[Dict[str, Any]]:
        return [TeamHandshakeSerializer.serialize_item(item) for item in queryset]
