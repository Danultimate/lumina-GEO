import sys

from firecrawl import Firecrawl

from lumina_geo.config import settings


class IngestionError(Exception):
    pass


def scrape_url(url: str) -> str:
    app = Firecrawl(api_key=settings.firecrawl_api_key)
    result = app.scrape(url, formats=["markdown"])

    if isinstance(result, dict):
        content = result.get("markdown", "").strip()
    else:
        content = (getattr(result, "markdown", None) or "").strip()

    if not content:
        raise IngestionError(
            f"Firecrawl returned empty content for URL: {url}"
        )

    print(f"[lumina-geo] Scraped {len(content)} characters from {url}", file=sys.stderr)
    return content
