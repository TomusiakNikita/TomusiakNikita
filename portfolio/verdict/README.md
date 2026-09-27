# VERDICT — Public Case Study

> Source code is private while the product is under active development. This page documents the architecture and engineering approach without exposing proprietary implementation details.

## Product

VERDICT is a **PC-only, Steam-first game discovery and review platform**.

The MVP is intentionally focused:

- PC games only
- Steam as the primary external source for discovery, metadata, and review enrichment
- Supabase as the canonical source of truth
- Redis as optional cache
- AI as an optional enhancement rather than a dependency for core page rendering

## Architecture

```text
Next.js web app
      │
      ├── Steam provider / ingestion
      │
      ├── Supabase / PostgreSQL
      │
      ├── optional Redis cache
      │
      └── FastAPI AI service
```

### Main components

- **Next.js application** for discovery, search, game pages, verdict UI, and review submission
- **FastAPI service** for optional summarization, fraud detection, fit scoring, and hardware guidance
- **Provider abstraction** around external game-data sources
- **Steam-first ingestion layer**
- **Supabase/PostgreSQL** for normalized application data
- **Shared TypeScript contracts** across application boundaries

## Data flow

1. Search checks the database-backed catalog first.
2. If a game is not already cached, the Steam provider is queried.
3. Opening a result ingests normalized Steam metadata into Supabase.
4. Subsequent page loads read from Supabase first.
5. Steam review aggregates and selected review entries are synced into dedicated tables.
6. VERDICT-owned scores remain separate from Steam sentiment.

## Engineering decisions

### Database-first reads

External APIs are useful for discovery and enrichment, but they should not become a hard dependency for every page load. Persisting normalized data provides:

- faster subsequent reads
- more predictable application behavior
- a stable internal data model
- easier extension to future providers

### Provider abstraction

Steam is the first provider, not the entire architecture. External-source logic is isolated behind a provider layer so future integrations do not require rewriting the application core.

### Optional infrastructure

Redis and AI services are enhancements rather than mandatory dependencies.

That keeps the MVP simpler to operate and reduces the number of external systems that can break core functionality.

### Separation of external sentiment and app-owned verdicts

Steam review data is stored separately from VERDICT's own recommendation and review data. This prevents external aggregate sentiment from being confused with the product's own scoring model.

## Technology

- Next.js
- TypeScript
- FastAPI
- Supabase / PostgreSQL
- Steam public storefront endpoints
- Optional Redis / Upstash
- Optional AI service

## What this project demonstrates

- SaaS architecture
- frontend/backend service boundaries
- database-first data design
- API integration
- provider abstractions
- data ingestion and normalization
- optional caching
- optional AI services
- keeping an MVP intentionally narrow

## Status

Active private project.
