from __future__ import annotations

from django.contrib import admin

from .models import ResumeDocument


@admin.register(ResumeDocument)
class ResumeDocumentAdmin(admin.ModelAdmin):
    list_display = ("file_name", "content_preview", "metadata_summary", "created_at", "updated_at")
    search_fields = ("file_name", "content")
    list_filter = ("created_at",)
    readonly_fields = ("created_at", "updated_at")
    list_per_page = 50

    @admin.display(description="Content preview")
    def content_preview(self, obj: ResumeDocument) -> str:
        text = obj.content or ""
        return (text[:80] + "...") if len(text) > 80 else text

    @admin.display(description="Metadata")
    def metadata_summary(self, obj: ResumeDocument) -> str:
        if not obj.metadata:
            return "{}"
        items = list(obj.metadata.items())
        preview = ", ".join(f"{k}: {v}" for k, v in items[:3])
        if len(items) > 3:
            preview += ", ..."
        return preview
