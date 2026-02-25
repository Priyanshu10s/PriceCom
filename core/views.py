from django.views.generic import TemplateView
from django.db import DatabaseError, OperationalError
from django.http import HttpResponseServerError
import logging
from typing import List, Dict, Any

from core.services.manager import get_coordinated_data

logger = logging.getLogger(__name__)

class ProductSearchView(TemplateView):
    template_name = "scraper/search_results.html"

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        search_query = self.request.GET.get('q', '')
        
        context['search_query'] = search_query
        context['results'] = []

        if search_query:
            try:
                # Fetch coordinated data via the orchestration layer
                context['results'] = get_coordinated_data(search_query)
            except (DatabaseError, OperationalError) as e:
                logger.error(f"Database error during search for '{search_query}': {e}")
                # Ideally, redirect to an error page or show a friendly message
                context['error'] = "A temporary database error occurred. Please try again later."
            except Exception as e:
                logger.exception(f"Unexpected error during search for '{search_query}': {e}")
                context['error'] = "An unexpected error occurred."
                
        return context
