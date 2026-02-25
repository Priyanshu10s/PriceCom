from decimal import Decimal
from typing import Dict, Any, Optional
from datetime import datetime
from .normalization import DataCleaningPipeline

class UnifiedDataMapper:
    """
    Transforms loosely scraped raw data into strictly defined keys.
    """
    
    @staticmethod
    def to_standard_units(value: Any, unit_type: str) -> Any:
        # Cross-Store Normalization
        if unit_type == 'price':
            return DataCleaningPipeline.clean_price(str(value))
        elif unit_type == 'rating':
            return DataCleaningPipeline.clean_rating(str(value))
        elif unit_type == 'date':
            # Handling relative delivery text
            return str(value)
        return value

    @staticmethod
    def map_store_data(raw_data: dict, store_name: str) -> Dict[str, Any]:
        """
        Heterogeneous Mapping Logic: Fixes raw dict outputs across scrapers 
        into standard standard Matrix view dependencies.
        """
        price = UnifiedDataMapper.to_standard_units(raw_data.get('price'), 'price')
        rating = UnifiedDataMapper.to_standard_units(raw_data.get('rating'), 'rating')
        
        return {
            'store': store_name,
            'title': raw_data.get('title', 'Unknown Product'),
            'price': float(price) if price else None,
            'url': raw_data.get('url', ''),
            'rating': rating,
            'delivery': raw_data.get('delivery', 'Standard Delivery'),
            'last_updated': raw_data.get('last_updated', datetime.now().isoformat())
        }
