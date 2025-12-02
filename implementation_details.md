# Project implementation details
## Project description
Builds a pipeline to ingest resumes, embed them with Ollama, store vectors in PostgreSQL/pgvector, and expose a minimal web UI/API for semantic and hybrid search.

## Resume ingestion process
- Supported sources: `.txt`, `.md`, `.json`, `.pdf` under `data/`.
- Pipeline reads files, extracts text/metadata, generates embeddings via Ollama, and stores `ResumeDocument` rows with vectors in Postgres.
- Deduplication by `file_name` with a DB index; existing filenames are skipped.
- Can run inline or enqueue via Celery (`run_ingestion --async`).

## Search methods
- Vector search (cosine) over embeddings.
- Hybrid search: vector shortlist + lexical re-rank on query keywords for better handling of explicit terms (years, tech names).
- Configurable Ollama models for embedding and generation via env vars.

## UI/UX considerations
- Simple HTML page with textarea prompt, method dropdown (vector/hybrid), AJAX submission, and result cards showing preview/metadata/similarity.
- Includes a sample expected JSON response for clarity and quick testing.

<img width="876" height="937" alt="image" src="https://github.com/user-attachments/assets/5db311be-335e-4190-b548-13314a2451ab" />


## Potential improvements
- More complex search process involving multiple steps. (e.g. Use language models to extract skill and requirements from the query before searching)
- Allow search refinement to improve search results by taking new prompt + current search results into account
- Better result pagination, filtering (skills/experience), and loading/error states.
- Automated tests for ingestion, embedding failures, and search ranking.
- Model fallback and smaller default models for low-resource environments.
- Preprocess and extract the skills and experiences from the resumes as part of the ingestion process
