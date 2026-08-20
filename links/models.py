import uuid

from django.conf import settings
from django.db import models


class ShortLink(models.Model):
    """A short link that redirects to a target URL."""

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='short_links')
    code = models.CharField(max_length=16, unique=True, blank=True)
    target = models.URLField()
    title = models.CharField(max_length=255, blank=True, default='')
    clicks = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'/{self.code} -> {self.target}'

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = uuid.uuid4().hex[:8]
        super().save(*args, **kwargs)
