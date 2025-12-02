# Job Candidate Seeker

Simple Django + pgvector project to ingest resumes, generate embeddings with Ollama, and perform semantic search via a small web UI.

## Requirements
- Docker and Docker Compose
- Ports: 5432 (Postgres), 6379 (Redis), 11434 (Ollama), 8000 (Web UI/API)
- System resources: minimum ~8 GB RAM for smaller embedding models; 16 GB+ recommended if using larger models (e.g., `gpt-oss:20b`) so the Ollama container has enough memory to load the model. Increase Docker Desktop memory accordingly.

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
- Open http://localhost:8000/search/ to load the HTML page with the prompt form and AJAX-powered results list.
- POSTing JSON `{"query": "<your requirements>"}` to `/search/` returns extracted criteria and ranked matches from pgvector.

## Environment configuration
Defaults are set in `docker-compose.yml` (e.g., `DATABASE_URL`, `OLLAMA_BASE_URL`, `OLLAMA_MODEL`). Override by exporting variables or editing the compose file if you need different models or database settings.
