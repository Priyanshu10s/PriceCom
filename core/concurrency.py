import threading
from typing import Callable, Any
from core.services import ScraperService

def run_scraper_async(url: str, store_name: str, callback: Callable[[Any], None] = None):
    """
    Runs the scraper in a separate thread to avoid blocking the main execution.
    A callback function can be provided to handle the result (e.g., logging or notifying).
    """
    def _target():
        service = ScraperService()
        data = service.fetch_product_data(url, store_name)
        product = service.save_product(data)
        
        if callback:
            callback(product if product else data)

    thread = threading.Thread(target=_target)
    thread.daemon = True # Daemon threads exit when the main program exits
    thread.start()
    return thread
