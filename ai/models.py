from django.conf import settings
from django.db import models


class Conversation(models.Model):
    """A chat conversation with the AI assistant."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ai_conversations')
    title = models.CharField(max_length=255, blank=True, default='')
    model = models.CharField(max_length=255, blank=True, default='')
    system_prompt = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return self.title or f'Conversation {self.id}'


class Message(models.Model):
    """A single message in an AI conversation."""

    ROLE_USER = 'user'
    ROLE_ASSISTANT = 'assistant'

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=20)
    content = models.TextField()
    attachment = models.FileField(upload_to='ai_uploads/%Y/%m/', null=True, blank=True)
    attachment_name = models.CharField(max_length=255, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.role}: {self.content[:50]}'
