import datetime
from django.utils import timezone
from typing import Optional

def get_utc_now() -> datetime.datetime:
    """
    Returns the current Aware UTC timestamp.
    Prevents Naive Datetime bugs.
    """
    return timezone.now()

def sync_api_timestamp(api_time_str: str) -> Optional[datetime.datetime]:
    """
    Parses an API timestamp string and converts it to a UTC-aware datetime object.
    Prevents "Offset Bugs" or "Future-Time" data.
    """
    if not api_time_str:
        return None
        
    try:
        # Expected format: ISO 8601 or similar (adjust based on actual API)
        # Using dateutil parser is robust, but let's stick to standard lib if possible or django utils
        from django.utils.dateparse import parse_datetime
        
        dt = parse_datetime(api_time_str)
        if dt is None:
             # Fallback logic or specific format parsing
             return None
             
        if timezone.is_naive(dt):
            # If naive, assume UTC or API source timezone (defaulting to UTC for safety)
            return timezone.make_aware(dt, timezone.utc)
        return dt.astimezone(timezone.utc)
        
    except (ValueError, TypeError):
        # Log error in production
        return None

def is_price_stale(last_updated: datetime.datetime, hours_threshold: int = 6) -> bool:
    """
    Checks if the price is older than the threshold.
    Use this for Safe Comparisons to avoid TypeError between Naive and Aware.
    """
    if not last_updated:
        return True
        
    now = get_utc_now()
    
    # Ensure comparison is safe
    if timezone.is_naive(last_updated):
         # This should ideally not happen if models are correct, but defensive coding:
         last_updated = timezone.make_aware(last_updated, timezone.utc)
         
    cutoff = now - datetime.timedelta(hours=hours_threshold)
    return last_updated < cutoff

def get_price_duration(last_updated: datetime.datetime) -> datetime.timedelta:
    """
    Calculates how long ago the price was updated.
    """
    if not last_updated:
        return datetime.timedelta(0)
        
    now = get_utc_now()
    if timezone.is_naive(last_updated):
        last_updated = timezone.make_aware(last_updated, timezone.utc)
        
    return now - last_updated
