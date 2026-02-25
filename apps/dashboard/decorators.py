from functools import wraps
from django.core.cache import cache
from django.http import JsonResponse, HttpResponseForbidden
from django.conf import settings

def rate_limit_cart(limit: int = 10, period: int = 60):
    """
    DoS Protection Layer for Cart Operations.
    Limits the number of "Add to Cart" requests to prevent scraper loop attacks or spam.
    Returns 429 Too Many Requests if exceeded.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Key based on user ID or IP Address
            identifier = request.user.id if request.user.is_authenticated else request.META.get('REMOTE_ADDR')
            cache_key = f"rate_limit_cart_{identifier}"
            
            # Fetch current request count
            request_count = cache.get(cache_key, 0)
            
            if request_count >= limit:
                return JsonResponse(
                    {'error': 'Too Many Requests. Please wait a moment.'}, 
                    status=429
                )
            
            # Increment and set expiry if it's the first request
            if request_count == 0:
                cache.set(cache_key, 1, timeout=period)
            else:
                # We can't elegantly increment and keep timeout in basic memcached without specific backend support, 
                # so cache.incr is used.
                try:
                    cache.incr(cache_key)
                except ValueError:
                    cache.set(cache_key, 1, timeout=period)
                    
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
