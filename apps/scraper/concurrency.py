from apps.scraper.tasks import scrape_product_task

def run_scraper_async(url: str, store_name: str, callback=None):
    """
    "Fire and Forget" Scraper Trigger.
    Offloads scraping to Celery Worker via Redis.
    """
    # Callback is ignored in async pattern as we rely on signals/db updates
    result = scrape_product_task.delay(url, store_name)
    return result
