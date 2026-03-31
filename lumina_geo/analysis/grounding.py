import json

from lumina_geo.analysis.base import BaseLens
from lumina_geo.reporting.models import GroundingResult

_INSTRUCTIONS = """
Analyze the content for the GROUNDING LENS.

1. Check if factual data (prices, specs, statistics) is stored in <table> or <ul> tags.
2. Check for JSON-LD Schema.org markup. Specifically identify which of these high-value types
   are present and which are missing:
   - FAQPage (for Q&A content)
   - HowTo (for step-by-step content)
   - Article or BlogPosting (must include datePublished and dateModified)
   - Product (with pricing and ratings)
   - Organization (entity recognition for the brand)
   - Review or AggregateRating
3. Rate "Citation Probability" from 1–10: how likely an AI search engine can cite this page reliably.
4. Determine is_groundable: true if an AI can reliably cite this page, false otherwise.
5. List schema_gaps as specific missing Schema.org types relevant to this page's content.
6. List critical_fixes ordered by citation impact — highest impact first.

Respond ONLY with this JSON structure:
{
  "score": <int 1-10>,
  "citation_probability": <int 1-10>,
  "is_groundable": <bool>,
  "findings": [<string>, ...],
  "critical_fixes": [<string>, ...],
  "schema_gaps": [<string>, ...]
}
"""


class GroundingLens(BaseLens):
    def analyze(self, content: str) -> GroundingResult:
        raw = self._call(content, _INSTRUCTIONS)
        data = json.loads(raw)
        return GroundingResult(**data)
