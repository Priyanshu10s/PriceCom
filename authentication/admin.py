"""
apps/accounts/admin.py
Admin configuration for Accounts app.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Admin configuration for Custom User Model.
    """
    model = User
    list_display = ('email', 'username', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'groups')
    search_fields = ('email', 'username')
    ordering = ('email',)

    # Use default UserAdmin fieldsets for now as we haven't added custom fields in models.py yet
