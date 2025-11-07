# MCP BacklinkContent Builder

MCP-svit för triadstyrd backlink-produktion med fokus på publication_domain × target_url × anchor_text.

## Översikt

Detta system implementerar en komplett MCP (Model Context Protocol) arkitektur för att automatisera och kvalitetssäkra produktion av backlink-innehåll. Systemet använder en deterministisk approach med preflight-planering, automatisk QC-validering och compliance-kontroller.

## Arkitektur

### MCP-servrar

1. **analysisdb** - Databasadapter för publicistprofiler, ankarpportföljer och händelseloggning
2. **collectors** - Datainsamlare för SERP, media-signaler och SEO-metriker (mock i v1)
3. **features** - Feature builders för entitetsgrafer och ankarportföljanalys
4. **preflight** - Preflight-planering och QC-validering för backlink-innehåll

### Teknisk Stack

- Python 3.11
- PostgreSQL 16
- Docker & Docker Compose
- MCP Server Python SDK
- Jinja2 för templating
- JSON Schema för validering

## Snabbstart

### Krav

- Docker & Docker Compose
- Python 3.11+ (för lokal utveckling)
- 4GB RAM minimum
- 10GB diskutrymme

### Installation

1. Klona repot:
```bash
git clone https://github.com/robwestz/mcp-blcwrtr.git
cd mcp-blcwrtr
```

2. Kopiera miljövariabler:
```bash
cp .env.example .env
```

3. Starta systemet:
```bash
docker compose up -d
```

4. Verifiera att allt körs:
```bash
docker compose ps
docker compose logs -f
# Vänta tills du ser "READY" från alla servrar
```

5. Testa databasanslutning:
```bash
docker compose exec analysisdb psql -U analysis -d analysisdb -c "SELECT 1;"
```

## Miljövariabler

Redigera `.env` med dina värden:

```env
# Databas
DATABASE_URL=postgresql://analysis:analysis@postgres:5432/analysisdb

# Externa API:er (mock_first mode i v1)
SERP_API_KEY=din_serp_nyckel_här      # Krävs ej i mock-läge
AHREFS_KEY=din_ahrefs_nyckel_här      # Optional
SEMRUSH_KEY=din_semrush_nyckel_här    # Optional

# Feature toggles
USE_MOCK_COLLECTORS=true               # Använd mock-data för collectors
USE_SUPABASE=false                     # Använd lokal Postgres

# Säkerhet
ALLOWED_DOMAINS=genline.se,happycasino.se
COMPETITOR_DOMAINS=casinoguide.se,bettingexpert.se
```

## MCP Gateway-konfiguration

För att använda verktygen via en MCP-klient, konfigurera din gateway att peka på `gateway/mcp-gateway.config.json`:

```bash
# Exempel med Claude Desktop eller annan MCP-klient
mcp-client --config ./gateway/mcp-gateway.config.json
```

## Tillgängliga Verktyg

### analysisdb

- `db.get_publisher_profile` - Hämta publicistprofil för domän
- `db.get_anchor_portfolio` - Analysera ankarportfölj för mål-URL
- `db.get_pages` - Lista sidor för kund eller inventarie
- `db.log_event` - Logga händelser för spårning

### collectors

- `serp.get_snapshot` - SERP-analys med intents och LSI-termer
- `media.signals` - Nyheter, video och podcast-signaler
- `ahrefs.metrics` - [Optional] Ahrefs SEO-metriker
- `semrush.metrics` - [Optional] Semrush SEO-metriker

### features

- `features.entity_graph` - Bygg entitetsgraf från seed-termer
- `features.anchor_portfolio.recalc` - Omberäkna ankarportfölj

### preflight

- `preflight.build` - Bygg preflight-matris från order
- `qc.validate` - Validera artikel mot QC-trösklar

## Exempel på Användning

### 1. Bygg Preflight för ny order

```json
{
  "tool": "preflight.build",
  "input": {
    "order": {
      "order_ref": "550e8400-e29b-41d4-a716-446655440000",
      "customer_id": "cust_001",
      "publication_domain": "genline.se",
      "target_url": "https://happycasino.se/casino",
      "anchor_text": "casino",
      "topic": "Så undviker du falska ledtrådar i släktforskningen",
      "constraints": {
        "word_count": 800,
        "tone": "informativ",
        "compliance": ["gambling"]
      }
    }
  }
}
```

### 2. Validera artikel

```json
{
  "tool": "qc.validate",
  "input": {
    "article_text": "## Rubrik\n\nInnehåll med [[casino]] länk...",
    "preflight_matrix": {...},
    "auto_fix": true
  }
}
```

## QC-validering

Systemet validerar mot följande trösklar:

- **LSI-termer**: Minst 6 unika termer inom ±2 meningar från ankaret
- **Trust-signaler**: Minst 1 trovärdig källa (T1/T2 föredras)
- **Ankarplacering**: Aldrig i rubriker, företrädesvis i mittpunkt
- **Compliance**: Branschspecifika disclaimers för reglerade områden

### Statusnivåer

- **APPROVED** (≥85 poäng): Redo för leverans
- **LIGHT_EDITS** (≥70 poäng): Mindre justeringar behövs
- **BLOCKED** (<70 poäng): Kritiska problem måste åtgärdas

## Utveckling

### Köra tester

```bash
# Alla tester
make test

# Specifik server
docker compose exec analysisdb pytest -v tests/

# Med coverage
docker compose exec analysisdb pytest --cov=src tests/
```

### Linting

```bash
make lint
```

### Databasmigrering

Placera SQL-filer i `infra/migrations/` och kör:

```bash
docker compose exec postgres psql -U analysis -d analysisdb -f /migrations/your_migration.sql
```

## Felsökning

### Vanliga Problem

**Problem: "READY" syns inte i loggarna**

Lösning:
```bash
# Kontrollera databas
docker compose exec postgres pg_isready

# Återskapa containers
docker compose down -v
docker compose up -d --build
```

**Problem: "ERR_DB_CONN" fel**

Lösning:
1. Verifiera DATABASE_URL i `.env`
2. Kontrollera att postgres-containern körs
3. Vänta 15 sekunder för databas-init

**Problem: Mock-data returneras trots API-nycklar**

Lösning:
```bash
# Sätt USE_MOCK_COLLECTORS=false
# Starta om collectors
docker compose restart collectors
```

### Loggar

```bash
# Alla loggar
docker compose logs -f

# Specifik server
docker compose logs -f preflight

# Sök efter fel
docker compose logs | grep ERROR
```

## Projektstruktur

```
mcp-blcwrtr/
├── docker-compose.yml       # Orkestrering
├── gateway/                 # MCP gateway-konfiguration
├── servers/                 # MCP-servrar
│   ├── analysisdb/         # Databasadapter
│   ├── collectors/         # Datainsamlare
│   ├── features/           # Feature builders  
│   └── preflight/          # Planering & QC
├── infra/                  # Infrastruktur
│   ├── db/init/           # Databas-schema
│   └── scripts/           # Hjälpskript
├── qc/                    # QC-konfiguration
└── kb/                    # Knowledge base
```

## Knowledge Base

Se `kb/`-mappen för detaljerad dokumentation om:

- Anchor risk optimization
- Publisher profiling 
- LSI och lemmatization
- E-E-A-T signaler
- Compliance-policys
- m.m.

## Bidra

1. Forka repot
2. Skapa feature branch (`git checkout -b feature/AmazingFeature`)
3. Committa ändringar (`git commit -m 'Add AmazingFeature'`)
4. Pusha till branch (`git push origin feature/AmazingFeature`)
5. Öppna Pull Request

## Licens

MIT License - se LICENSE-filen för detaljer.

## Support

För frågor och support:
- Skapa en GitHub issue
- Kontakta teamet via projektsidan

## Changelog

Se [CHANGELOG.md](CHANGELOG.md) för versionshistorik.
