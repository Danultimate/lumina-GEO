# Lumina-GEO

Audit any website or code repository for AI search readiness. Lumina-GEO scores your content across four lenses — Grounding, Semantic Hierarchy, Answer-First, and Authority — and tells you exactly what to fix to get cited by Google AI Overviews, ChatGPT, and Perplexity.

## Table of Contents

- [Key Features](#key-features)
- [How It Works](#how-it-works)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [Architecture](#architecture)
- [Environment Variables](#environment-variables)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)

---

## Key Features

- **Four Analysis Lenses** — Grounding, Semantic Hierarchy, Answer-First, and Authority, each scored 1–10
- **Platform-Specific Scores** — Separate weighted scores for Google AI Overviews and ChatGPT/Perplexity
- **AI Bot Access Check** — Detects if GPTBot, PerplexityBot, ClaudeBot, Google-Extended, or Bingbot are blocked in `robots.txt`
- **Schema.org Detection** — Identifies missing structured data (FAQPage, HowTo, Article, Product, etc.)
- **Dual Interface** — CLI for developers, FastAPI HTTP API for integrations
- **Web Dashboard** — Single-page UI served alongside the API
- **Two Report Formats** — Machine-readable JSON and human-readable Markdown
- **Repo Auditing** — Point it at a local directory to audit HTML/JSX/TSX source files

---

## How It Works

```
Target (URL or path)
        │
        ▼
  ┌─────────────┐
  │  Ingestion  │  URL → Firecrawl scrape → Markdown
  │             │  Path → LangChain file loader → concatenated text
  └──────┬──────┘
         │
         ▼
  ┌─────────────────────────────────────────┐
  │              Analysis (Gemini AI)        │
  │                                          │
  │  GroundingLens     SemanticHierarchy     │
  │  AnswerFirstLens   AuthorityLens         │
  └──────────────────┬──────────────────────┘
                     │
         ┌───────────┴────────────┐
         │                        │
         ▼                        ▼
  Robots.txt check          Composite + Platform
  (deterministic,           score calculation
   no AI call)
         │                        │
         └───────────┬────────────┘
                     │
                     ▼
              AuditReport
         (report.json + report.md)
```

**Scoring weights:**

| Platform | Grounding | Semantic | Answer-First | Authority |
|---|---|---|---|---|
| Google AI Overviews | 35% | 30% | 20% | 15% |
| ChatGPT / Perplexity | 25% | 15% | 25% | 35% |

If AI crawler bots are blocked in `robots.txt`, both platform scores are capped at 3.0 regardless of content quality.

---

## Tech Stack

- **Language:** Python 3.11+
- **API Framework:** FastAPI + Uvicorn
- **CLI:** Typer
- **Data Models:** Pydantic v2 + pydantic-settings
- **LLM:** Google Gemini (via `google-generativeai`, temperature=0 for determinism)
- **Web Scraping:** Firecrawl v2 (`firecrawl-py`)
- **Repo Loading:** LangChain + LangChain Community
- **Frontend:** Vanilla HTML/CSS/JS (no framework), served as static files
- **Deployment:** Docker + docker-compose

---

## Prerequisites

- Python 3.11 or higher
- Docker and docker-compose (for containerised deployment)
- A [Google Gemini API key](https://aistudio.google.com/app/apikey)
- A [Firecrawl API key](https://www.firecrawl.dev/) (required for URL auditing)

---

## Getting Started

### 1. Clone the repository

```bash
git clone git@github.com:Danultimate/lumina-GEO.git
cd lumina-GEO
```

### 2. Set up environment variables

```bash
cp .env.example .env
```

Edit `.env` and fill in your API keys:

```
GEMINI_API_KEY=your_gemini_api_key_here
FIRECRAWL_API_KEY=your_firecrawl_api_key_here
```

See [Environment Variables](#environment-variables) for all options.

### 3a. Run with Docker (recommended)

```bash
docker-compose up --build
```

The API and dashboard will be available at `http://localhost:1818`.

### 3b. Run locally without Docker

```bash
pip install -r requirements.txt
uvicorn api.main:app --reload --port 8000
```

Or use the CLI directly:

```bash
pip install -e .
lumina-geo audit https://example.com
```

---

## Usage

### Web Dashboard

Open `http://localhost:1818` in your browser. Enter any URL or local path and click **Audit**. The dashboard shows:

- Composite score (1–10)
- Platform scores for Google AI Overviews and ChatGPT/Perplexity
- AI bot access status (which crawlers are blocked)
- Per-lens scores with findings, critical fixes, and specific gaps
- Authority signals breakdown (named author, statistics, expert quotes, dates, citations)
- PDF export button

### CLI

```bash
# Audit a URL
lumina-geo audit https://example.com

# Audit a local repository
lumina-geo audit ./path/to/project

# Save reports to a specific directory
lumina-geo audit https://example.com --output-dir ./reports
```

Output files written to `--output-dir`:
- `report.json` — full structured report
- `report.md` — human-readable markdown report

### API

**Audit endpoint**

```
POST /audit
Content-Type: application/json

{
  "target": "https://example.com",
  "output_dir": "./reports"
}
```

Response: full `AuditReport` JSON object.

**Health check**

```
GET /health
→ {"status": "ok"}
```

**Example with curl:**

```bash
curl -X POST http://localhost:1818/audit \
  -H "Content-Type: application/json" \
  -d '{"target": "https://example.com", "output_dir": "./reports"}'
```

---

## Architecture

### Directory Structure

```
lumina-GEO/
├── cli.py                        # Typer CLI entry point
├── api/
│   ├── main.py                   # FastAPI app, static mount, health check
│   └── routes/
│       └── audit.py              # POST /audit route
├── lumina_geo/
│   ├── __init__.py               # build_report() — main orchestration function
│   ├── config.py                 # pydantic-settings config (reads .env)
│   ├── analysis/
│   │   ├── base.py               # BaseLens abstract class + _strip_fences()
│   │   ├── grounding.py          # Grounding Lens (schema, structured data)
│   │   ├── semantic_hierarchy.py # Semantic Hierarchy Lens (H1–H4 flow)
│   │   ├── answer_first.py       # Answer-First Lens (H2/H3 self-contained answers)
│   │   ├── authority.py          # Authority Lens (author, stats, quotes, dates)
│   │   └── robots_check.py       # Deterministic robots.txt AI bot check
│   ├── ingestion/
│   │   ├── url_scraper.py        # Firecrawl v2 URL → markdown
│   │   └── repo_loader.py        # LangChain local file loader (.html/.tsx/.jsx)
│   ├── llm/
│   │   └── gemini_client.py      # Gemini API client, exponential backoff, temp=0
│   └── reporting/
│       ├── models.py             # Pydantic models for all results and the AuditReport
│       └── writer.py             # report.json + report.md writer
├── static/
│   └── index.html                # Single-page dashboard (no framework)
├── tests/
│   ├── analysis/                 # Unit tests per lens
│   ├── ingestion/                # Ingestion unit tests
│   ├── reporting/                # Writer unit tests
│   ├── fixtures/                 # sample.html + sample.md
│   ├── test_api.py               # FastAPI TestClient integration tests
│   └── test_cli.py               # CLI runner tests
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

### Analysis Lenses

Each lens extends `BaseLens`, calls Gemini with a structured prompt, and returns a typed Pydantic model.

| Lens | What It Checks | Key Output Fields |
|---|---|---|
| **Grounding** | JSON-LD schema types, structured data in tables/lists, citation probability | `schema_gaps`, `is_groundable`, `citation_probability` |
| **Semantic Hierarchy** | Logical H1→H4 flow, heading hierarchy, topic coherence | `logic_breaks` |
| **Answer-First** | Every H2/H3 opens with a 40–60 word self-contained answer | `missing_definitions` |
| **Authority** | Named author, statistics with sources, expert quotes, dates, external citations | `has_named_author`, `has_statistics`, `has_expert_quotes`, `has_date_signals`, `has_external_citations`, `authority_signals` |

The robots.txt check is deterministic — it uses `urllib.robotparser` and makes no AI calls.

### LLM Reliability

- All Gemini calls use `temperature=0` for deterministic, consistent scores
- Exponential backoff with jitter: up to 5 retries (`wait = 2^attempt + random(0,1)`)
- LLM responses are stripped of markdown fences before JSON parsing
- Repo auditing is capped at 800,000 characters (safe for Gemini 1.5 Pro's 1M token context window)

---

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `GEMINI_API_KEY` | Yes | — | Google Gemini API key |
| `FIRECRAWL_API_KEY` | Yes | — | Firecrawl API key (required for URL targets) |
| `GEMINI_MODEL` | No | `gemini-1.5-pro` | Gemini model to use |
| `OUTPUT_DIR` | No | `.` | Default directory for report output |

> **Note:** `FIRECRAWL_API_KEY` is only called when auditing a URL. Local repo audits do not use Firecrawl.

---

## Deployment

### Docker (Recommended)

```bash
# First-time setup
cp .env.example .env
# Edit .env with your API keys

docker-compose up -d --build
```

The service runs on port `1818` and restarts automatically unless stopped. Reports are written to `./reports` on the host (mounted as a volume).

**Update to latest version:**

```bash
git pull
docker-compose down && docker-compose up -d --build
```

### VPS / Manual

```bash
# Clone
git clone git@github.com:Danultimate/lumina-GEO.git /docker/lumina-geo
cd /docker/lumina-geo

# Configure
cp .env.example .env
nano .env   # add GEMINI_API_KEY and FIRECRAWL_API_KEY

# Build and start
docker-compose up -d --build
```

### Without Docker

```bash
pip install -r requirements.txt
uvicorn api.main:app --host 0.0.0.0 --port 1818
```

---

## Troubleshooting

**`Firecrawl returned empty content`**

The URL may be blocking Firecrawl's crawler. Try a different URL or check the site's `robots.txt`. Some JavaScript-heavy SPAs may also return empty content if Firecrawl can't render them.

**`JSON.parse: unexpected character` in the dashboard**

The Gemini model returned a malformed response. This is handled automatically via fence-stripping, but if it persists, check that your `GEMINI_API_KEY` is valid and the model quota hasn't been exceeded.

**Inconsistent scores across runs**

Ensure `temperature=0` is set in `lumina_geo/llm/gemini_client.py`. Scores should be fully deterministic across identical inputs.

**`Invalid API key` / `UnauthorizedError`**

Double-check your `.env` file on the server. The environment variables must be present when the container starts — rebuild after any `.env` changes:

```bash
docker-compose down && docker-compose up -d --build
```

**Container fails to start after `docker-compose up`**

Check logs for the error:

```bash
docker-compose logs lumina-geo
```

Common causes: missing API keys in `.env`, port 1818 already in use.

**Port conflict**

Change the host port in `docker-compose.yml`:

```yaml
ports:
  - "YOUR_PORT:8000"
```
