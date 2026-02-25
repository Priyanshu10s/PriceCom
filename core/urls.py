from django.urls import path
from .views import ProductSearchView

app_name = 'scraper'

urlpatterns = [
    path('search/', ProductSearchView.as_view(), name='product_search'),
]
