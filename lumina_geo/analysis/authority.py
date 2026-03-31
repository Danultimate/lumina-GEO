import json

from lumina_geo.analysis.base import BaseLens
from lumina_geo.reporting.models import AuthorityResult

_INSTRUCTIONS = """
Analyze the content for the AUTHORITY LENS.

AI systems prefer sources they can trust and verify. Evaluate how authoritative and
citable this content appears to AI search engines.

1. Check if there is a named author with credentials or expertise signals.
2. Check if statistics or data points are present with cited sources (e.g. "According to X, 47% of...").
3. Check if expert quotes with attribution (name + title/organisation) are present.
4. Check if publication date or last-updated date signals are present.
5. Check if there are external links to authoritative sources (research papers, government sites, industry bodies).
6. Score from 1–10 (10 = highly authoritative, well-cited, expert-attributed content).
7. List authority_signals found — what positive authority elements exist.
8. List critical_fixes ordered by citation impact — highest impact first.

Respond ONLY with this JSON structure:
{
  "score": <int 1-10>,
  "has_named_author": <bool>,
  "has_statistics": <bool>,
  "has_expert_quotes": <bool>,
  "has_date_signals": <bool>,
  "has_external_citations": <bool>,
  "authority_signals": [<string>, ...],
  "findings": [<string>, ...],
  "critical_fixes": [<string>, ...]
}
"""


class AuthorityLens(BaseLens):
    def analyze(self, content: str) -> AuthorityResult:
        raw = self._call(content, _INSTRUCTIONS)
        data = json.loads(raw)
        return AuthorityResult(**data)
