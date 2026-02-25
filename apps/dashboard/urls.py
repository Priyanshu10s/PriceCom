from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

app_name = 'dashboard'

# [FORCE LOGIC] Route & Permission Alignment
# Strictly protecting all private dashboard routes with login_required
urlpatterns = [
    path('', views.dashboard_home, name='dashboard-home'),
    
    # Secure Non-Enumerable Routes (UUIDs)
    path('product/<uuid:uuid>/', views.ProductDetailView.as_view(), name='product_detail'),
    
    # Intelligence Layer
    path('redirect/', login_required(views.redirect_to_merchant), name='redirect_to_merchant'),
    
    # Scraper/Core features moved to Dashboard
    path('search/', login_required(views.ProductSearchView.as_view()), name='product_search'),
    path('task_status/<str:task_id>/', login_required(views.TaskStatusView.as_view()), name='task_status'),
    path('api/history/<int:product_id>/', login_required(views.PriceHistoryAPIView.as_view()), name='price_history_api'),
]
