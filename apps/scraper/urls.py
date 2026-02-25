from django.urls import path
from django.urls import path
from .views import ProductSearchView, TaskStatusView, WatchlistView, ToggleWatchlistView, PriceHistoryAPIView

app_name = 'scraper'

urlpatterns = [
    path('search/', ProductSearchView.as_view(), name='product_search'),
    path('task_status/<str:task_id>/', TaskStatusView.as_view(), name='task_status'),
    path('watchlist/', WatchlistView.as_view(), name='watchlist'),
    path('watchlist/toggle/', ToggleWatchlistView.as_view(), name='toggle_watchlist'),
    path('api/history/<int:product_id>/', PriceHistoryAPIView.as_view(), name='price_history_api'),
]
