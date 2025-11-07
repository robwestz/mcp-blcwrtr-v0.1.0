#!/bin/bash
# Bootstrap script for MCP BacklinkContent system

set -e

echo "Starting MCP BacklinkContent bootstrap..."

# Wait for postgres to be ready
echo "Waiting for PostgreSQL to be ready..."
until pg_isready -h postgres -p 5432 -U analysis; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 2
done

echo "PostgreSQL is ready!"

# Run database initialization if needed
if [ "${RUN_DB_INIT}" = "true" ]; then
    echo "Running database initialization..."
    psql -h postgres -U analysis -d analysisdb -f /docker-entrypoint-initdb.d/01_schema.sql
    echo "Database initialization complete!"
fi

# Signal readiness
echo "READY: Bootstrap complete"
