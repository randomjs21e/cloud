import uuid

from django.conf import settings
from django.db import models


class Survey(models.Model):
    """A survey/form created by a user."""

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='surveys')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    requires_account = models.BooleanField(default=False)
    token = models.CharField(max_length=64, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = uuid.uuid4().hex
        super().save(*args, **kwargs)


class Question(models.Model):
    """A question inside a survey."""

    TYPE_TEXT = 'text'
    TYPE_TEXTAREA = 'textarea'
    TYPE_CHOICE = 'choice'
    TYPE_MULTI = 'multi'
    TYPE_RATING = 'rating'
    TYPE_CHOICES = [
        (TYPE_TEXT, 'Qısa mətn'),
        (TYPE_TEXTAREA, 'Uzun mətn'),
        (TYPE_CHOICE, 'Tək seçim'),
        (TYPE_MULTI, 'Çox seçim'),
        (TYPE_RATING, 'Qiymətləndirmə (1-5)'),
    ]

    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='questions')
    text = models.CharField(max_length=500)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default=TYPE_TEXT)
    options = models.TextField(blank=True, default='')  # newline-separated for choice/multi
    required = models.BooleanField(default=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.text

    def option_list(self):
        return [o for o in self.options.split('\n') if o.strip()]


class Response(models.Model):
    """A single submission of a survey."""

    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='responses')
    respondent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='survey_responses')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Cavab #{self.id}'


class Answer(models.Model):
    """An answer to a question within a response."""

    response = models.ForeignKey(Response, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    value = models.TextField(blank=True, default='')

    def __str__(self):
        return f'{self.question.text}: {self.value}'
