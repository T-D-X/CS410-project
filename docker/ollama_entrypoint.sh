#!/bin/sh
set -e

EMBED_MODEL="${OLLAMA_EMBED_MODEL:-nomic-embed-text}"
GENERATE_MODEL="${OLLAMA_GENERATE_MODEL:-gpt-oss:20b}"
    
ollama serve &
pid="$!"

# Give the server a moment to start before pulling the model
sleep 3
ollama pull "$EMBED_MODEL"
ollama pull "$GENERATE_MODEL"

wait "$pid"
