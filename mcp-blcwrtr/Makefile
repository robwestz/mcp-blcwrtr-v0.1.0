.PHONY: up down logs db-init test lint pack clean

# Starta alla containers
up:
	docker compose up -d --build

# Stoppa och rensa alla containers
down:
	docker compose down -v

# Visa loggar från alla containers
logs:
	docker compose logs -f

# Initiera databasen (körs automatiskt vid start)
db-init:
	docker compose exec postgres psql -U analysis -d analysisdb -f /docker-entrypoint-initdb.d/01_schema.sql

# Kör alla tester
test:
	@echo "Running smoke tests..."
	docker compose exec analysisdb pytest -v tests/
	docker compose exec collectors pytest -v tests/
	docker compose exec features pytest -v tests/
	docker compose exec preflight pytest -v tests/

# Kör linting (om ruff är installerat)
lint:
	@echo "Running linters..."
	find servers -name "*.py" | xargs ruff check || true

# Packa projektet som ZIP
pack:
	@echo "Creating project archive..."
	zip -r mcp-blcwrtr.zip . -x ".git/*" -x "venv/*" -x "__pycache__/*" -x "*.pyc" -x ".env" -x "postgres_data/*"
	@echo "Archive created: mcp-blcwrtr.zip"

# Rensa genererade filer
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + || true
	find . -type f -name "*.pyc" -delete || true
	rm -f mcp-blcwrtr.zip
