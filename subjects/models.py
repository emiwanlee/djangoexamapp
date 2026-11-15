from django.db import models
from django.conf import settings


class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.code})"


class SchemeOfWork(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="schemes")
    title = models.CharField(max_length=200)
    class_level = models.CharField(max_length=50, blank=True)
    term = models.CharField(max_length=50, blank=True)
    session = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.subject.name} - {self.title}"


class Topic(models.Model):
    scheme = models.ForeignKey(SchemeOfWork, on_delete=models.CASCADE, related_name="topics")
    title = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=1)
    objectives = models.TextField(blank=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.title


class Note(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="notes")
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title