import re
import json
import requests
from typing import Any

from django.conf import settings
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from pipeline.models import ResumeDocument
from pgvector.django import CosineDistance


def _format_result(doc, similarity: float | None, html_format=True) -> dict[str, Any]:
    content_preview = (doc.content[:300] + "...") if len(doc.content) > 300 else doc.content
    if html_format:
        content_preview = re.sub(r"\n+", "<br>", content_preview)

    return {
        "candidate_id": doc.id,
        "file_name": doc.file_name,
        "metadata": doc.metadata,
        "content_preview": content_preview,
        "similarity": similarity,
    }


def generate_embedding(text: str) -> list[float]:
    url = f"{settings.OLLAMA_BASE_URL}{settings.EMBEDDINGS_ENDPOINT}"
    payload = {"model": settings.OLLAMA_EMBED_MODEL, "prompt": text}
    response = requests.post(url, json=payload, timeout=settings.OLLAMA_REQUEST_TIMEOUT)
    response.raise_for_status()
    embedding = response.json().get("embedding")
    if not embedding:
        raise ValueError(f"No embedding returned from Ollama for model {settings.OLLAMA_EMBED_MODEL}")
    return [float(value) for value in embedding]


def parse_json_block(raw_text: str) -> dict[str, Any]:
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        # Try to locate the first JSON object if extra text is present
        start = raw_text.find("{")
        end = raw_text.rfind("}") + 1
        if 0 <= start < end:
            try:
                return json.loads(raw_text[start:end])
            except json.JSONDecodeError:
                pass
    return {}


# def extract_candidate_requirements(prompt: str) -> dict[str, list[str]]:
#     url = f"{settings.OLLAMA_BASE_URL}{settings.GENERATE_ENDPOINT}"
#     generation_prompt = (
#         "Given the user's hiring request, list the target skills, experience, and education. "
#         "Respond with JSON using keys skills, experience, and education, each an array of strings. "
#         f"User request: {prompt}"
#     )
#     response = requests.post(
#         url,
#         json={"model": settings.OLLAMA_GENERATE_MODEL, "prompt": generation_prompt, "stream": False},
#         timeout=settings.OLLAMA_REQUEST_TIMEOUT,
#     )
#     response.raise_for_status()
#     raw_text = response.json().get("response") or response.text
#     parsed = parse_json_block(raw_text)
#     return {
#         "skills": parsed.get("skills", []),
#         "experience": parsed.get("experience", []),
#         "education": parsed.get("education", []),
#         "raw": raw_text,
#     }


def search_candidates(query_embedding: list[float], limit: int = 10) -> list[dict[str, Any]]:
    documents = (
        ResumeDocument.objects.annotate(distance=CosineDistance("embedding", query_embedding))
        .order_by("distance")[:limit]
    )
    results: list[dict[str, Any]] = []
    for doc in documents:
        distance = getattr(doc, "distance", None)
        similarity = 1 - float(distance) if distance is not None else None
        results.append(_format_result(doc, similarity))
    return results


def hybrid_search_candidates(
    query_text: str, query_embedding: list[float], limit: int = 10, shortlist: int = 30, lexical_weight: float = 0.35
) -> list[dict[str, Any]]:
    """
    Two-stage hybrid search:
    1. Vector shortlist using cosine distance.
    2. Re-rank shortlist by combining vector similarity with simple lexical overlap.
    """
    keywords = [tok.lower() for tok in query_text.replace(",", " ").split() if len(tok.strip()) > 2]

    candidates = (
        ResumeDocument.objects.annotate(distance=CosineDistance("embedding", query_embedding))
        .order_by("distance")[:shortlist]
    )

    scored = []
    for doc in candidates:
        distance = getattr(doc, "distance", None)
        base_similarity = 1 - float(distance) if distance is not None else 0.0

        lexical_hits = 0
        if keywords:
            content_lower = doc.content.lower()
            lexical_hits = sum(content_lower.count(kw) for kw in keywords)
        lexical_score = min(1.0, lexical_hits / max(1, len(keywords)))

        combined_score = (base_similarity * (1 - lexical_weight)) + (lexical_score * lexical_weight)
        scored.append((combined_score, _format_result(doc, base_similarity)))

    scored.sort(key=lambda item: item[0], reverse=True)
    return [item[1] for item in scored[:limit]]


def bm25_search_candidates(query_text: str, limit: int = 10) -> list[dict[str, Any]]:
    """
    Lexical/BM25-style search using PostgreSQL full-text ranking.
    """
    vector = SearchVector("content", config="english")
    query = SearchQuery(query_text, search_type="plain", config="english")
    documents = (
        ResumeDocument.objects.annotate(rank=SearchRank(vector, query))
        .filter(rank__gt=0)
        .order_by("-rank")[:limit]
    )
    results = []
    for doc in documents:
        rank = getattr(doc, "rank", None)
        results.append(_format_result(doc, rank, html_format=True))
    return results
