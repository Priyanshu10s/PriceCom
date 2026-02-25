from django import template
from django.utils import timezone
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.utils.safestring import mark_safe
import datetime

register = template.Library()

@register.filter
def smart_freshness(value: datetime.datetime) -> str:
    """
    Apply a "Just Now" threshold to timestamps.
    Eliminates future-time bugs and adds a pulsing indicator for fresh data.
    """
    if not value:
        return ""
        
    try:
        now = timezone.now()
        # Latency Shield: Use absolute difference to handle slight clock skew
        # If the scraper runs perfectly but DB write lags by ms, value might be slightly > now if not careful,
        # or if scraper sets time slightly in future (unlikely with auto_now but possible with manual overrides).
        # We rely on now - value.
        delta = now - value
        
        # The 30-Second Rule
        if abs(delta.total_seconds()) < 30:
            # Return "Just now" with Pulsing Green CSS class
            # We use mark_safe because we are returning HTML
            return mark_safe('<span class="text-successGreen font-bold animate-pulse">Just now</span>')
            
        # Fallback to standard naturaltime
        return naturaltime(value)
        
    except (ValueError, TypeError):
        return value
