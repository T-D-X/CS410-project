from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Iterable

import requests
from PyPDF2 import PdfReader
from celery import shared_task
from django.conf import settings
from django.db import transaction

from .models import ResumeDocument

logger = logging.getLogger(__name__)
SUPPORTED_EXTENSIONS = {".txt", ".md", ".json", ".pdf"}
EMBEDDINGS_ENDPOINT = "/api/embeddings"


def list_resume_files(directory: Path) -> Iterable[Path]:
    for path in sorted(directory.rglob("*")):
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
            yield path


def extract_pdf_content(file_path: Path) -> tuple[str, dict[str, object]]:
    try:
        reader = PdfReader(str(file_path))
    except Exception as exc:
        raise ValueError(f"Could not read PDF {file_path.name}: {exc}") from exc

    pages: list[str] = []
    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        if text.strip():
            pages.append(text)

    content = "\n".join(pages).strip()
    if not content:
        raise ValueError(f"No extractable text found in PDF {file_path.name}")

    metadata: dict[str, object] = {"source": file_path.name, "page_count": len(reader.pages)}
    return content, metadata


def gather_resume_data(file_path: Path) -> dict[str, object]:
    suffix = file_path.suffix.lower()
    if suffix == ".json":
        payload = json.loads(file_path.read_text(encoding="utf-8"))
        content = payload.get("content") or payload.get("resume_text") or json.dumps(payload, indent=2)
        metadata = {k: v for k, v in payload.items() if k not in {"content", "resume_text"}}
    elif suffix == ".pdf":
        content, metadata = extract_pdf_content(file_path)
    else:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        metadata = {"source": file_path.name}

    return {
        "file_name": file_path.name,
        "content": content,
        "metadata": metadata,
    }


def generate_embedding(text: str) -> list[float]:
    base_url = settings.OLLAMA_BASE_URL.rstrip("/")
    url = f"{base_url}{EMBEDDINGS_ENDPOINT}"
    payload = {"model": settings.OLLAMA_EMBED_MODEL, "prompt": text}
    response = requests.post(url, json=payload, timeout=settings.OLLAMA_REQUEST_TIMEOUT)
    response.raise_for_status()
    body = response.json()
    embedding = body.get("embedding")
    if not embedding:
        raise ValueError(f"No embedding returned from Ollama for model {settings.OLLAMA_EMBED_MODEL}")

    if len(embedding) != settings.EMBEDDING_DIMENSION:
        raise ValueError(
            f"Embedding dimension mismatch: received {len(embedding)} but settings specify {settings.EMBEDDING_DIMENSION}"
        )

    return [float(value) for value in embedding]


def store_resume(data: dict[str, object]) -> bool:
    if ResumeDocument.objects.filter(file_name=data["file_name"]).exists():
        logger.info("Skipping %s; file already ingested", data["file_name"])
        return False

    embedding = generate_embedding(data["content"])
    with transaction.atomic():
        ResumeDocument.objects.create(
            file_name=data["file_name"],
            content=data["content"],
            metadata=data.get("metadata", {}),
            embedding=embedding,
        )
    return True


def ingest_directory(directory: Path) -> dict[str, object]:
    processed = 0
    errors: list[str] = []
    if not directory.exists():
        msg = f"Data directory {directory} does not exist"
        logger.error(msg)
        return {"processed": processed, "errors": [msg]}

    for file_path in list_resume_files(directory):
        try:
            resume_data = gather_resume_data(file_path)
            created = store_resume(resume_data)
            if created:
                processed += 1
        except Exception as exc:  # pragma: no cover - defensive logging
            error_msg = f"Failed to ingest {file_path.name}: {exc}"
            logger.exception(error_msg)
            errors.append(error_msg)

    return {"processed": processed, "errors": errors}


@shared_task(bind=True, name="pipeline.ingest_resumes")
def ingest_resumes_task(self, data_directory: str | None = None) -> dict[str, object]:
    directory = Path(data_directory) if data_directory else settings.DATA_DIRECTORY
    result = ingest_directory(directory)
    logger.info(
        "Ingestion completed by task %s with %s processed and %s errors",
        self.request.id,
        result["processed"],
        len(result["errors"]),
    )
    return result
