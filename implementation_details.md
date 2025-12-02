# Project implementation details
<img width="876" height="937" alt="image" src="https://github.com/user-attachments/assets/5db311be-335e-4190-b548-13314a2451ab" />

## Project description
Builds a pipeline to ingest resumes, embed them with Ollama, store vectors in PostgreSQL/pgvector, and expose a minimal web UI/API for semantic and hybrid search.

## Resume ingestion process
- Supported sources: `.txt`, `.md`, `.json`, `.pdf` under `data/`.
- Pipeline reads files, extracts text/metadata, generates embeddings via Ollama, and stores `ResumeDocument` rows with vectors in Postgres.
- Deduplication by `file_name` with a DB index; existing filenames are skipped.
- Can run inline or enqueue via Celery (`run_ingestion --async`).

## Search methods
Here are the details of each supported search method and observations:

### Vector search (cosine)
- Implementation: pgvector `CosineDistance` annotated on `ResumeDocument.embedding`, ordered ascending, then similarity calculated as `1 - distance`.
- When to use: general semantic matching and recall of resumes that paraphrase the query.

### Hybrid search (vector + lexical)
- Implementation: vector shortlist by cosine, then re-rank with a combined score of vector similarity and lexical overlap (keyword counts normalized and weighted).
- When to use: queries with explicit terms (years, tools) where you want both semantic and exact term emphasis.
- Tunables: shortlist size, lexical weight, stopword handling.

### BM25 / lexical search
- Implementation: PostgreSQL full-text search via `SearchVector` + `SearchRank` on `content` (english config), ordered by rank.
- When to use: precision on exact terms/numbers, lightweight retrieval without embeddings.

All methods configurable via query payload (`method`: vector | hybrid | bm25); embedding model via env (`OLLAMA_EMBED_MODEL`).

## UI/UX considerations
- Simple HTML page with textarea prompt, method dropdown (vector/hybrid), AJAX submission, and result cards showing preview/metadata/similarity.
- Includes a sample expected JSON response for clarity and quick testing.

## Potential improvements
- More complex search process involving multiple steps. (e.g. Use language models to extract skill and requirements from the query before searching)
- Allow search refinement to improve search results by taking new prompt + current search results into account
- Better result pagination, filtering (skills/experience), and loading/error states.
- Automated tests for ingestion, embedding failures, and search ranking.
- Model fallback and smaller default models for low-resource environments.
- Preprocess and extract the skills and experiences from the resumes as part of the ingestion process
