import sys

from firecrawl import Firecrawl

from lumina_geo.config import settings


class IngestionError(Exception):
    pass


def scrape_url(url: str) -> str:
    app = Firecrawl(api_key=settings.firecrawl_api_key)
    result = app.scrape(url, formats=["markdown"])

    content = result.get("markdown", "").strip() if isinstance(result, dict) else ""

    if not content:
        raise IngestionError(
            f"Firecrawl returned empty content for URL: {url}"
        )

    print(f"[lumina-geo] Scraped {len(content)} characters from {url}", file=sys.stderr)
    return content
