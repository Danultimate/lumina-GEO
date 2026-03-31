import json

from lumina_geo.analysis.base import BaseLens
from lumina_geo.reporting.models import AnswerFirstResult

_INSTRUCTIONS = """
Analyze the content for the ANSWER-FIRST LENS.

AI systems extract passages, not pages. Every section should open with a self-contained statement.

1. Identify ALL H2 and H3 headings (not just question headings).
2. For each heading, check if a concise 40–60 word self-contained answer or definition
   immediately follows it — one that makes sense without surrounding context.
3. Give special weight to question-based headings (ending in "?" or phrased as questions)
   — these must have a direct answer immediately following.
4. List ALL headings that lack a direct self-contained answer as "missing_definitions".
5. Score from 1–10 (10 = every heading opens with a standalone 40–60 word answer block).
6. List critical_fixes ordered by citation impact — highest impact first.

Respond ONLY with this JSON structure:
{
  "score": <int 1-10>,
  "findings": [<string>, ...],
  "critical_fixes": [<string>, ...],
  "missing_definitions": [<string>, ...]
}
"""


class AnswerFirstLens(BaseLens):
    def analyze(self, content: str) -> AnswerFirstResult:
        raw = self._call(content, _INSTRUCTIONS)
        data = json.loads(raw)
        return AnswerFirstResult(**data)
