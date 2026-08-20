from django.contrib import admin

from .models import File


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'size', 'share_type', 'created_at')
    list_filter = ('share_type', 'owner')
    search_fields = ('name',)
