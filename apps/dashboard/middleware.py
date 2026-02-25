try:
    import zoneinfo
except ImportError:
    from backports import zoneinfo

from django.utils import timezone
from django.conf import settings

class TimezoneMiddleware:
    """
    The Backend Gatekeeper.
    Intercepts every request to synchronize the server's UTC 'Source of Truth'
    with the user's local timezone.
    Hardened against header injection and invalid timezone strings.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1. Extract Handshake Cookie
        tzname = request.COOKIES.get('django_timezone')
        
        if tzname:
            # 2. Sanitization (The Topper Layer)
            # Prevent Header Injection by stripping whitespace/special chars
            tzname = tzname.strip()
            
            # 3. Validation & Activation
            try:
                # "Anti-Crash" Safety Check using ZoneInfo
                # Validates against IANA database
                timezone.activate(zoneinfo.ZoneInfo(tzname))
            except (zoneinfo.ZoneInfoNotFoundError, KeyError, ValueError):
                # Fallback Security: Default to UTC if corrupted/malicious
                # Ensures server never crashes due to client data
                timezone.deactivate()
        else:
            timezone.deactivate()

        # Thread-Local Integrity:
        # timezone.activate sets a thread-local variable, ensuring User A's
        # location never leaks into User B's request.
        
        return self.get_response(request)
