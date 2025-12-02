#!/bin/sh
set -e

EMBED_MODEL="${OLLAMA_EMBED_MODEL:-nomic-embed-text}"
    
ollama serve &
pid="$!"

# Give the server a moment to start before pulling the model
sleep 3
ollama pull "$EMBED_MODEL"

wait "$pid"
