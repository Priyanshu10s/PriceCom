from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # api/register/
    path('register/', views.register_view, name='register'),
    # api/login/
    # api/login/
    path('login/', auth_views.LoginView.as_view(template_name='authentication/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    # Password Reset Flow
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
]
