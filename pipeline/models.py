from django.conf import settings
from django.db import models
from pgvector.django import VectorField


class ResumeDocument(models.Model):
    file_name = models.CharField(max_length=255, unique=True)
    content = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)
    embedding = VectorField(dimensions=getattr(settings, "EMBEDDING_DIMENSION", 384))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["file_name"]
        indexes = [models.Index(fields=["file_name"], name="resume_file_name_idx")]

    def __str__(self):
        return self.file_name
