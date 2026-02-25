from django.utils import timezone

def server_time(request):
    """
    Injects the 'Golden Source' Server UTC Timestamp into every template.
    Ensures 100% synchronization between backend and frontend.
    """
    return {
        'server_now': timezone.now()
    }
