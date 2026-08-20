from django.conf import settings
from django.db import models


class EmailMessage(models.Model):
    """An email sent between platform users (Gmail-style)."""

    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_emails')
    recipients = models.ManyToManyField(settings.AUTH_USER_MODEL, through='EmailRecipient', related_name='emails')
    subject = models.CharField(max_length=255, blank=True, default='')
    body = models.TextField(blank=True, default='')
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-sent_at']

    def __str__(self):
        return self.subject or '(başlıqsız)'


class EmailRecipient(models.Model):
    """Per-recipient state for an email (read/starred/deleted)."""

    email = models.ForeignKey(EmailMessage, on_delete=models.CASCADE, related_name='recipient_links')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='email_links')
    is_read = models.BooleanField(default=False)
    is_starred = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)

    class Meta:
        unique_together = ('email', 'user')

    def __str__(self):
        return f'{self.user} <- {self.email}'
