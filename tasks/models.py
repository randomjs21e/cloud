from django.conf import settings
from django.db import models


class TaskList(models.Model):
    """A user's task list (Google Tasks-style)."""

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='task_lists')
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Task(models.Model):
    """A single task within a list."""

    PRIORITY_LOW = 'low'
    PRIORITY_MED = 'med'
    PRIORITY_HIGH = 'high'
    PRIORITY_CHOICES = [
        (PRIORITY_LOW, 'Aşağı'),
        (PRIORITY_MED, 'Orta'),
        (PRIORITY_HIGH, 'Yüksək'),
    ]

    task_list = models.ForeignKey(TaskList, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=255)
    notes = models.TextField(blank=True, default='')
    done = models.BooleanField(default=False)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default=PRIORITY_MED)
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['done', '-priority', 'due_date', 'created_at']

    def __str__(self):
        return self.title
