from django.db import models
from django.conf import settings


class StudentProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    class_level = models.CharField(max_length=50, blank=True)
    school = models.CharField(max_length=150, blank=True)

    def __str__(self):
        return self.user.username