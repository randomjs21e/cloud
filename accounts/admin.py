from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'plan', 'storage_limit_mb', 'is_staff')
    list_filter = ('plan', 'is_staff', 'is_superuser')
    fieldsets = UserAdmin.fieldsets + (
        ('Plan', {'fields': ('plan', 'storage_limit_mb')}),
    )
