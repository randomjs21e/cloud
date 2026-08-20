from django.contrib import admin

from .models import Contact


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'phone', 'email', 'company')
    list_filter = ('owner',)
    search_fields = ('name', 'phone', 'email')
