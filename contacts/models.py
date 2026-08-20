from django.conf import settings
from django.db import models


class Contact(models.Model):
    """A contact stored by a user (Google Contacts style)."""

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='contacts')
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=30, blank=True, default='')
    email = models.EmailField(blank=True, default='')
    company = models.CharField(max_length=255, blank=True, default='')
    address = models.CharField(max_length=255, blank=True, default='')
    notes = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def linked_user(self):
        """A registered user whose phone matches this contact's phone."""
        if not self.phone:
            return None
        from accounts.models import User
        return User.objects.filter(phone=self.phone).exclude(pk=self.owner_id).first()
