from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model."""

    PLAN_CHOICES = [
        ('free', 'Pulsuz'),
        ('pro', 'Pro'),
        ('business', 'Biznes'),
    ]
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='free')
    plan_expires_at = models.DateTimeField(null=True, blank=True)
    storage_limit_mb = models.IntegerField(default=2048)
    phone = models.CharField(max_length=30, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    def is_plan_active(self):
        """True if the user has an active paid plan (not expired)."""
        if self.plan == 'free':
            return True
        if self.plan_expires_at is None:
            return True
        from django.utils import timezone
        return self.plan_expires_at > timezone.now()

    def __str__(self):
        return self.email or self.username
