from django.contrib import admin

from .models import PaymentRecord


@admin.register(PaymentRecord)
class PaymentRecordAdmin(admin.ModelAdmin):
    list_display = ('type', 'user', 'amount', 'plan', 'processed', 'created_at')
    list_filter = ('type', 'plan', 'processed')
    search_fields = ('user__username', 'user__email', 'message_id')
