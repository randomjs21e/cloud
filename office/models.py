from django.conf import settings
from django.db import models


class OfficeFile(models.Model):
    """An online-editable office document (doc / sheet / slides)."""

    TYPE_DOC = 'doc'
    TYPE_SHEET = 'sheet'
    TYPE_SLIDES = 'slides'
    TYPE_CHOICES = [
        (TYPE_DOC, 'Sənəd'),
        (TYPE_SHEET, 'Cədvəl'),
        (TYPE_SLIDES, 'Slayd'),
    ]

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='office_files')
    title = models.CharField(max_length=255)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default=TYPE_DOC)
    content = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return self.title
