import re
from decimal import Decimal
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class UnifiedProduct:
    """Standard Python Object mapping heterogeneous data streams."""
    title: str
    price: Optional[Decimal]
    rating: Optional[float]
    store_name: str
    last_updated: str
    url: str

class CleanDataService:
    """
    High-Performance Data Normalization Engine.
    Transforms 'Dirty Data' into unified Python objects.
    """

    @staticmethod
    def to_decimal(price_str: Any) -> Optional[Decimal]:
        """
        Regex sanitization to strip currency symbols and commas.
        Returns a Python Decimal for 100% mathematical accuracy.
        """
        if not price_str:
            return None
        
        string_val = str(price_str)
        # Regex to strip ₹, $, commas, and non-numeric chars
        cleaned = re.sub(r'[^\d.]', '', string_val)
        
        try:
            return Decimal(cleaned)
        except Exception:
            return None

    @staticmethod
    def to_float(rating_str: Any) -> Optional[float]:
        """Extracts float ratings from strings like '4.5 out of 5 stars'."""
        if not rating_str:
            return None
            
        match = re.search(r"(\d+(\.\d+)?)", str(rating_str))
        if match:
            return float(match.group(1))
        return None

class UnifiedSchemaMapper:
    """
    Heterogeneous Data Normalization logic mapping Amazon/Flipkart keys.
    """
    @staticmethod
    def map_store_data(raw_data: dict, store_name: str) -> UnifiedProduct:
        # Dynamically pulls keys relying on dict.get or standard fallbacks
        price = CleanDataService.to_decimal(raw_data.get('price'))
        rating = CleanDataService.to_float(raw_data.get('rating'))
        
        return UnifiedProduct(
            title=raw_data.get('title', 'Unknown Product'),
            price=price,
            rating=rating,
            store_name=store_name,
            last_updated=raw_data.get('last_updated', ''),
            url=raw_data.get('url', '')
        )
