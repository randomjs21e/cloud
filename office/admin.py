from django.contrib import admin

from .models import OfficeFile


@admin.register(OfficeFile)
class OfficeFileAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'owner', 'updated_at')
    list_filter = ('type', 'owner')
    search_fields = ('title',)
