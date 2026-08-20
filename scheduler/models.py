import uuid

from django.conf import settings
from django.db import models


class ScheduleLink(models.Model):
    """A user's public booking link (Calendly-style)."""

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='schedule_links')
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=64, unique=True, blank=True)
    duration_minutes = models.IntegerField(default=30)
    description = models.TextField(blank=True, default='')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = uuid.uuid4().hex[:8]
        super().save(*args, **kwargs)


class Booking(models.Model):
    """A meeting booked through a schedule link."""

    schedule = models.ForeignKey(ScheduleLink, on_delete=models.CASCADE, related_name='bookings')
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, default='')
    notes = models.TextField(blank=True, default='')
    start_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['start_time']

    def __str__(self):
        return f'{self.name} @ {self.start_time}'
