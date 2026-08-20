from django.conf import settings
from django.db import models


class ChatGroup(models.Model):
    """A chat group (WhatsApp style)."""

    name = models.CharField(max_length=255)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owned_chat_groups')
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Membership', related_name='chat_groups')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Membership(models.Model):
    """A user's membership in a chat group."""

    group = models.ForeignKey(ChatGroup, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_memberships')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('group', 'user')

    def __str__(self):
        return f'{self.user} in {self.group}'


class Conversation(models.Model):
    """A private 1-on-1 chat between two users."""

    user1 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='conversations_as_1')
    user2 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='conversations_as_2')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user1', 'user2')

    def __str__(self):
        return f'{self.user1} <-> {self.user2}'

    def other(self, user):
        return self.user2 if user == self.user1 else self.user1

    @classmethod
    def get_or_create_between(cls, a, b):
        conv = cls.objects.filter(user1=a, user2=b).first() or cls.objects.filter(user1=b, user2=a).first()
        if conv:
            return conv
        return cls.objects.create(user1=a, user2=b)


class Message(models.Model):
    """A message in a chat group or private conversation."""

    TYPE_TEXT = 'text'
    TYPE_IMAGE = 'image'
    TYPE_FILE = 'file'
    TYPE_VOICE = 'voice'
    TYPE_CONTACT = 'contact'
    TYPE_CHOICES = [
        (TYPE_TEXT, 'Mətn'),
        (TYPE_IMAGE, 'Şəkil'),
        (TYPE_FILE, 'Fayl'),
        (TYPE_VOICE, 'Səs'),
        (TYPE_CONTACT, 'Kontakt'),
    ]

    group = models.ForeignKey(ChatGroup, on_delete=models.CASCADE, related_name='messages', null=True, blank=True)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages', null=True, blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='group_chat_messages')
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default=TYPE_TEXT)
    body = models.TextField(blank=True, default='')
    attachment = models.FileField(upload_to='chat_uploads/%Y/%m/', blank=True, null=True)
    contact_name = models.CharField(max_length=255, blank=True, default='')
    contact_phone = models.CharField(max_length=30, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.author}: {self.body[:30]}'
