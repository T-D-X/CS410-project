FROM postgres:16

# Install pgvector extension for PostgreSQL 16
RUN apt-get update \
    && apt-get install -y --no-install-recommends postgresql-16-pgvector \
    && rm -rf /var/lib/apt/lists/*

# PostgreSQL stores initialization scripts inside this directory.
# The docker-compose file mounts SQL files into /docker-entrypoint-initdb.d
# to enable extensions or seed schema/data on first run.
