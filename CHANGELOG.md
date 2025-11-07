# Changelog

All notable changes to the MCP BacklinkContent Builder project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-11-01

### Added
- Initial release of MCP BacklinkContent Builder
- Four MCP servers implemented:
  - **analysisdb**: Database adapter for publisher profiles and anchor portfolios
  - **collectors**: SERP and media signal collectors (mock mode in v1)
  - **features**: Entity graph and anchor portfolio analysis
  - **preflight**: Content planning and QC validation
- PostgreSQL database schema with idempotent initialization
- Docker Compose orchestration for all services
- Comprehensive QC validation system with AUTO_FIX_ONCE policy
- Preflight matrix generation with:
  - Midpoint bridging concept
  - LSI term requirements (6-10 terms)
  - Trust signal integration
  - Compliance guards for regulated industries
- Mock implementations for external APIs (SERP, Ahrefs, Semrush)
- JSON Schema validation for all tool inputs/outputs
- Jinja2 templating for writer prompts
- Knowledge base documentation:
  - Anchor risk optimization strategies
  - Publisher profiling guide
  - LSI and lemmatization policies
  - E-E-A-T signal catalog
  - Compliance requirements
- Smoke tests for all servers
- MCP gateway configuration
- Comprehensive README with examples

### Security
- Environment-based secret management
- No hardcoded credentials
- Competitor blocking via trust registry
- PII protection in logging

### Known Issues
- External API integrations (SERP, Ahrefs, Semrush) are mocked
- Vector database support (pgvector) not implemented in v1
- Redis caching not implemented
- Limited auto-fix capabilities in QC validation

## [Unreleased]

### Planned for v0.2.0
- Real SERP API integration
- Ahrefs/Semrush API adapters
- pgvector support for semantic search
- Redis caching layer
- Extended auto-fix capabilities
- Batch processing support
- API rate limiting with circuit breakers
- Monitoring and metrics (Prometheus/Grafana)
- Webhook notifications
- Multi-language support (EN, NO, DK, FI)

### Planned for v0.3.0
- Machine learning models for:
  - Anchor risk prediction
  - LSI term generation
  - Content quality scoring
- A/B testing framework
- Advanced competitor analysis
- Content performance tracking
- Automated content optimization

### Planned for v1.0.0
- Production-ready external API integrations
- Horizontal scaling support
- Advanced caching strategies
- Complete test coverage (>90%)
- Performance optimizations
- Comprehensive API documentation
- Enterprise features:
  - Multi-tenancy
  - Role-based access control
  - Audit logging
  - SLA monitoring
