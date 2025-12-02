# Job Candidate Seeker

Simple Django project to ingest resumes, generate embeddings with Ollama, and perform semantic search via a small web UI.

For implementation details, refer to [implementation_details.md](https://github.com/T-D-X/CS410-project/blob/master/implementation_details.md)

## Requirements
- Docker and Docker Compose
- Ports: 5432 (Postgres), 6379 (Redis), 11434 (Ollama), 8000 (Web UI/API)
- System resources: ~8 GB RAM recommended for the `nomic-embed-text` model; ensure Docker Desktop allocates enough memory for the Ollama container to load the model.

## Environment
Environment variables are loaded from `.env` (ignored by git). A sample is provided in `.sample-env`:
```bash
cp .sample-env .env
```
Adjust values if you need different models or credentials.

These values are loaded as defaults in `docker-compose.yml` (e.g., `DATABASE_URL`, `OLLAMA_BASE_URL`, `OLLAMA_MODEL`). Override by modifying the .env.

## Services (docker-compose.yml)
- **db**: PostgreSQL 16 with `pgvector` extension enabled for vector storage and similarity search.
- **redis**: Message broker and result backend for Celery.
- **ollama**: Embedding/generation model host. Default model is `nomic-embed-text` (configure via `OLLAMA_MODEL`).
- **web**: Django/DRF app served by uvicorn (`jobsearch.asgi`). Exposes health check and search UI/API.
- **worker**: Celery worker that can run ingestion asynchronously.

## Quick start
```bash
docker-compose build
docker-compose up
```
The web app will be available at http://localhost:8000 (search UI at `/search/`, health check at `/health/`).

## First-time setup inside the web container
Open a shell in the running web container:
```bash
docker-compose exec web bash
```
Run migrations:
```bash
python manage.py migrate
```

## Ingest resumes
Place source files in `data/` (supports `.txt`, `.md`, `.json`, `.pdf`). Then run:
```bash
python manage.py run_ingestion --directory data
```
To enqueue ingestion to Celery instead of running inline:
```bash
python manage.py run_ingestion --directory data --async
```

## Search UI/API
- Open http://127.0.0.1:8000/search/ to load the HTML page with the prompt form, method dropdown, and AJAX-powered results list.
- POSTing JSON to `/search/`:
  ```json
  { "query": "<your requirements>", "method": "vector|hybrid|bm25" }
  ```
  - `vector`: cosine similarity over embeddings
  - `hybrid`: vector shortlist re-ranked with lexical overlap
  - `bm25`: PostgreSQL full-text/BM25-style lexical search
  
  Response includes `results` and echoes the chosen `method`.
