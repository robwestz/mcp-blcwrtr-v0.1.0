#!/bin/bash
# Healthcheck script for MCP BacklinkContent system

set -e

# Check PostgreSQL
check_postgres() {
    pg_isready -h ${DB_HOST:-postgres} -p ${DB_PORT:-5432} -U ${DB_USER:-analysis} > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "✓ PostgreSQL is healthy"
        return 0
    else
        echo "✗ PostgreSQL is not responding"
        return 1
    fi
}

# Check if database schema exists
check_schema() {
    PGPASSWORD=${DB_PASSWORD:-analysis} psql -h ${DB_HOST:-postgres} -U ${DB_USER:-analysis} -d ${DB_NAME:-analysisdb} \
        -c "SELECT 1 FROM information_schema.tables WHERE table_name = 'customers' LIMIT 1;" > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "✓ Database schema is initialized"
        return 0
    else
        echo "✗ Database schema not found"
        return 1
    fi
}

# Check MCP servers
check_mcp_server() {
    local server_name=$1
    local container_name="mcp-${server_name}"
    
    # Check if container is running
    if docker ps --format '{{.Names}}' | grep -q "^${container_name}$"; then
        # Check for READY log
        if docker logs "${container_name}" 2>&1 | grep -q "READY"; then
            echo "✓ ${server_name} server is ready"
            return 0
        else
            echo "✗ ${server_name} server is not ready"
            return 1
        fi
    else
        echo "✗ ${server_name} container is not running"
        return 1
    fi
}

# Run all checks
echo "=== MCP BacklinkContent Health Check ==="
echo "Timestamp: $(date)"
echo "----------------------------------------"

HEALTH_STATUS=0

# Database checks
check_postgres || HEALTH_STATUS=1
check_schema || HEALTH_STATUS=1

# Server checks (only if running in Docker environment)
if [ -n "$(docker ps -q 2>/dev/null)" ]; then
    check_mcp_server "analysisdb" || HEALTH_STATUS=1
    check_mcp_server "collectors" || HEALTH_STATUS=1
    check_mcp_server "features" || HEALTH_STATUS=1
    check_mcp_server "preflight" || HEALTH_STATUS=1
fi

echo "----------------------------------------"

if [ $HEALTH_STATUS -eq 0 ]; then
    echo "Overall status: HEALTHY ✓"
else
    echo "Overall status: UNHEALTHY ✗"
fi

exit $HEALTH_STATUS
