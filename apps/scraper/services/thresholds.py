from decimal import Decimal
from typing import Dict, Union, Optional

def is_meaningful_drop(previous_price: Decimal, current_price: Decimal) -> bool:
    """
    Hybrid Threshold Model: Signal-to-Noise Filter.
    Mathematically distinguishes between 'Market Noise' and 'True Signals'.
    
    The "MacBook vs. Earphone" Paradox Solver:
    - High-ticket items (MacBook): 3% drop is significant money.
    - Low-ticket items (Earphones): 3% drop is pennies; need absolute ₹100 floor.
    
    Returns True only if the drop is actionable.
    """
    # Safety Check: Price Hike Protection
    if current_price >= previous_price:
        return False

    drop_amount = previous_price - current_price
    
    # Avoid division by zero
    if previous_price == 0:
        return False
        
    drop_percentage = (drop_amount / previous_price) * 100

    # Gate A: Relative Threshold (Active for expensive items)
    is_relative_signal = drop_percentage >= Decimal('3.0')

    # Gate B: Absolute Floor (Active for cheap items)
    is_absolute_signal = drop_amount >= Decimal('100.00')

    # Smart Filtering Logic:
    # For High-Ticket items (> ₹10,000), a ₹100 drop is noise (0.1%).
    # We insist on the Relative Signal for expensive items.
    HIGH_TICKET_THRESHOLD = Decimal('10000.00')
    
    if previous_price > HIGH_TICKET_THRESHOLD:
        # High Ticket: Must match Relative Threshold (e.g. 3% of 1L is ₹3k)
        # OR a very significant absolute drop (e.g. ₹1000) - but let's stick to % for now to be safe against noise
        # Actually, let's say if it's high ticket, we ONLY care about %, OR a much higher absolute (like ₹500?)
        # For this specific "MacBook Noise" test failure (1% drop of 1L = ₹1000), it failed because 1000 > 100.
        # So we must Disable is_absolute_signal if price is High.
        return is_relative_signal
    
    # Low/Mid Ticket: OR Logic applies
    return is_relative_signal or is_absolute_signal

def calculate_drop_metrics(previous_price: Decimal, current_price: Decimal) -> Dict[str, Union[Decimal, float]]:
    """
    Returns precise drop metrics for email templates.
    """
    if current_price >= previous_price or previous_price == 0:
        return {
            'actual_drop_amount': Decimal('0.00'),
            'drop_percentage': 0.0
        }
    
    drop_amount = previous_price - current_price
    drop_percentage = (drop_amount / previous_price) * 100
    
    return {
        'actual_drop_amount': drop_amount,
        'drop_percentage': round(float(drop_percentage), 2)
    }
