from __future__ import annotations

from django.contrib import admin

from .models import ResumeDocument


@admin.register(ResumeDocument)
class ResumeDocumentAdmin(admin.ModelAdmin):
    list_display = ("file_name", "created_at", "updated_at")
    search_fields = ("file_name", "content")
