from django.conf import settings
from django.db import models


class PaymentRecord(models.Model):
    """Log of a Ko-fi payment webhook event."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                             on_delete=models.SET_NULL, related_name='payments')
    message_id = models.CharField(max_length=100, blank=True, default='')
    type = models.CharField(max_length=30, blank=True, default='')
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    tier_name = models.CharField(max_length=100, blank=True, default='')
    plan = models.CharField(max_length=20, blank=True, default='')
    raw_data = models.TextField(blank=True, default='')
    processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.type} {self.amount} ({self.user})'
