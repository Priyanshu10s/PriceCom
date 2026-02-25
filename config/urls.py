from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    # Path is 'api/' exactly as requested.
    # This means accounts urls will be appended to 'api/'.
    path('accounts/', include('authentication.urls')), 
    path('scraper/', include('core.urls')),
    path('dashboard/', include('apps.dashboard.urls')),
    # Social Auth
    path('accounts/', include('allauth.urls')),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
]
