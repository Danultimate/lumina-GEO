# Lumina-GEO — Design Document

**Version:** 1.0  
**Date:** 2026-03-31  
**Status:** Approved — Ready for Implementation

---

## Understanding Summary

- **What:** A Python-based CLI and FastAPI tool that audits websites (via URL) and local code repositories for AI-Readability and Generative Engine Optimization (GEO)
- **Why:** To help developers and SEO professionals understand how well their content and markup will be interpreted, cited, and surfaced by AI-powered search engines
- **Who:** Two equal personas — developers auditing repos they own, and SEO professionals auditing URLs they may not own
- **Key constraints:** Dual first-class interfaces (CLI + API), self-hosted deployment, no auth, modular architecture (scrapers / analyzers / reporters separated)
- **Non-goals:** No user authentication, no cloud/SaaS deployment, no web UI or frontend

---

## Assumptions

1. Gemini API key and Firecrawl API key are provided via environment variables
2. The FastAPI server and CLI share the same core analysis logic — no duplication
3. Rate limiting is handled with exponential backoff on Gemini API calls only
4. Large repos that exceed Gemini's context window are truncated with a warning to stderr
5. No database — reports are file-based only (`report.json` + `report.md`)
6. URL vs local path is detected via `startswith("http")` — simple and sufficient
7. Gemini calls are always mocked in tests — no live API calls in CI

---

## Project Structure

```
lumina-geo/
├── lumina_geo/
│   ├── __init__.py
│   ├── config.py
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── url_scraper.py
│   │   └── repo_loader.py
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── grounding.py
│   │   ├── semantic_hierarchy.py
│   │   └── answer_first.py
│   ├── reporting/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   └── writer.py
│   └── llm/
│       ├── __init__.py
│       └── gemini_client.py
├── api/
│   ├── __init__.py
│   ├── main.py
│   └── routes/
│       └── audit.py
├── cli.py
├── pyproject.toml
├── .env.example
└── tests/
    ├── fixtures/
    ├── ingestion/
    ├── analysis/
    ├── reporting/
    ├── test_cli.py
    └── test_api.py
```

---

## Data Flow

```
Input: URL or directory path
          │
          ▼
    ┌─────────────┐
    │  Ingestion  │
    │  URL?       │──→ firecrawl.scrape() → Markdown string
    │  Repo?      │──→ LangChain loader  → Context Map string
    └─────┬───────┘
          │ raw_content: str
          ▼
    ┌─────────────────────────────────┐
    │         Analysis Engine         │
    │  GroundingLens.analyze()        │──→ GroundingResult
    │  SemanticHierarchyLens.analyze()│──→ SemanticHierarchyResult
    │  AnswerFirstLens.analyze()      │──→ AnswerFirstResult
    │  (sequential, with backoff)     │
    └─────┬───────────────────────────┘
          │
          ▼
    ┌─────────────┐
    │  Reporter   │
    │  composite_score = avg(3 scores)
    │  AuditReport (Pydantic)         │
    │  → report.json                  │
    │  → report.md                    │
    └─────────────┘
```

---

## Pydantic Output Schema

```python
class LensResult(BaseModel):
    score: int                       # 1–10
    findings: List[str]
    critical_fixes: List[str]

class GroundingResult(LensResult):
    schema_gaps: List[str]
    is_groundable: bool
    citation_probability: int        # 1–10

class SemanticHierarchyResult(LensResult):
    logic_breaks: List[str]

class AnswerFirstResult(LensResult):
    missing_definitions: List[str]

class AuditReport(BaseModel):
    url_or_path: str
    composite_score: float           # avg of three lens scores
    grounding: GroundingResult
    semantic_hierarchy: SemanticHierarchyResult
    answer_first: AnswerFirstResult
    generated_at: str                # ISO 8601
```

---

## Key Component Designs

### Gemini Client
- Single wrapper in `lumina_geo/llm/gemini_client.py`
- Exponential backoff: `wait = (2 ** attempt) + random.uniform(0, 1)`, max 5 retries
- Model configurable via `GEMINI_MODEL` env var, default `gemini-1.5-pro`

### Analysis Lenses
- All extend `BaseLens` (ABC) with a single `analyze(content: str) -> LensResult` method
- `SYSTEM_PROMPT` defined once on base class: `"Act as a Search Engine LLM Crawler analyzing content for GEO readiness."`
- JSON parsing of LLM response inside each `analyze()` method
- Lens calls are sequential (not parallel) for simpler rate limit management

### Configuration
- `pydantic-settings` with `.env` file support
- Required: `GEMINI_API_KEY`, `FIRECRAWL_API_KEY`
- Optional: `GEMINI_MODEL` (default: `gemini-1.5-pro`), `OUTPUT_DIR` (default: `.`)

### CLI
- Built with Typer
- Entry point: `lumina-geo audit <target> [--output-dir <path>]`
- `<target>` is a URL or local directory path

### FastAPI
- Single route: `POST /audit` accepting `{ "target": str, "output_dir": str }`
- Returns full `AuditReport` as JSON response

---

## Edge Cases

| Scenario | Handling |
|---|---|
| Firecrawl returns empty Markdown | Raise `IngestionError` before hitting Gemini |
| LLM returns malformed JSON | Catch `ValidationError`, retry once, then raise |
| Repo has zero matching files | Raise `IngestionError` early |
| Repo exceeds Gemini context window | Truncate with warning to stderr |
| API key missing | `pydantic-settings` raises at startup |
| `output_dir` doesn't exist | Create with `Path.mkdir(parents=True, exist_ok=True)` |

---

## Testing Strategy

- All Gemini calls mocked — no live API calls in tests
- Fixture content in `tests/fixtures/` — sample HTML and Markdown
- Coverage: ingestion, each lens, reporter, CLI runner, FastAPI TestClient

---

## Decision Log

| # | Decision | Alternatives | Rationale |
|---|---|---|---|
| 1 | Name: Lumina-GEO | Lumina-SEO | GEO is the core emphasis |
| 2 | CLI + API both first-class | CLI-first or API-first | Neither is subordinate |
| 3 | Shared core, independent interfaces | API-first + CLI as HTTP client | Only approach satisfying dual first-class |
| 4 | Self-hosted, no auth | API key, OAuth | Private network trust |
| 5 | LangChain retained | Plain pathlib | Future extensibility for chunking/embeddings |
| 6 | Gemini model configurable | Hardcoded | Upgrade without code changes |
| 7 | Equal weight scoring | Weighted, separate-only | Simplest correct default |
| 8 | All files analyzed recursively | Capped, user-specified | Matches requirement; truncation handles limits |
| 9 | Sequential lens calls | Parallel | Simpler error handling and rate limit management |
| 10 | pydantic-settings | python-dotenv + os.getenv | Centralized, typed, validated at startup |
| 11 | Gemini always mocked in tests | Live API calls | Deterministic, fast, no API cost in CI |
