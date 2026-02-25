from decimal import Decimal
import re

def clean_price_string(price_str: str) -> Decimal:
    """
    Converts a price string like "₹89,900" or "89,900.00" into a Decimal.
    Removes currency symbols and commas.
    """
    if not price_str:
        return Decimal("0.00")
        
    # Remove all non-numeric characters except the decimal point
    clean_str = re.sub(r'[^\d.]', '', price_str)
    
    try:
        return Decimal(clean_str)
    except Exception:
        return Decimal("0.00")
