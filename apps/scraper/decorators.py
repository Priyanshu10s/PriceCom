
import time
from functools import wraps
from django.core.cache import cache
from django.http import HttpResponseForbidden

def simple_ratelimit(key_prefix, limit=5, period=60):
    """
    Simple rate limiting decorator using Django cache.
    Limit: checks per 'period' seconds.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return view_func(request, *args, **kwargs) # Skip for anon or handle differently
                
            ip = request.META.get('REMOTE_ADDR')
            user_id = request.user.id
            cache_key = f"ratelimit:{key_prefix}:{user_id}:{ip}"
            
            # Get current count
            count = cache.get(cache_key, 0)
            
            if count >= limit:
                return HttpResponseForbidden("Rate limit exceeded. Please try again later.")
            
            # Increment and set expiry if new
            if count == 0:
                cache.set(cache_key, 1, period)
            else:
                cache.incr(cache_key)
                
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
