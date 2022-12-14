from django.db import models


class TimestampedModel(models.Model):
    added_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        abstract = True
        ordering = ['-added_at', '-updated_at']