import uuid

from django.conf import settings
from django.db import models


class Meeting(models.Model):
    """A Jitsi video meeting room."""

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='meetings')
    title = models.CharField(max_length=255)
    room = models.CharField(max_length=64, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.room:
            self.room = 'cloud-' + uuid.uuid4().hex[:12]
        super().save(*args, **kwargs)


class MeetingInvite(models.Model):
    """A user invited to a meeting."""

    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='invites')
    invitee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='meeting_invites')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('meeting', 'invitee')

    def __str__(self):
        return f'{self.invitee} -> {self.meeting}'
