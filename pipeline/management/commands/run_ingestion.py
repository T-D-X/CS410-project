from __future__ import annotations

from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from pipeline.tasks import ingest_directory, ingest_resumes_task


class Command(BaseCommand):
    help = (
        "Gather resume data, generate embeddings, and store the results either by running inline "
        "or by scheduling the Celery task."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--directory",
            type=str,
            default=None,
            help="Override the directory containing resume files (defaults to settings.DATA_DIRECTORY)",
        )
        parser.add_argument(
            "--async",
            dest="use_async",
            action="store_true",
            help="Enqueue the ingestion Celery task instead of running inline",
        )

    def handle(self, *args, **options):
        directory = Path(options.get("directory") or settings.DATA_DIRECTORY)
        if options.get("use_async"):
            result = ingest_resumes_task.delay(str(directory))
            self.stdout.write(
                self.style.SUCCESS(
                    f"Enqueued ingestion task {result.id} for directory {directory}. Use celery backend to monitor."
                )
            )
            return

        result = ingest_directory(directory)
        processed = result["processed"]
        errors = result["errors"]
        if errors:
            for err in errors:
                self.stderr.write(self.style.ERROR(err))
        self.stdout.write(self.style.SUCCESS(f"Processed {processed} files from {directory}"))
