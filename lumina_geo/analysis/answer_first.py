import json

from lumina_geo.analysis.base import BaseLens
from lumina_geo.reporting.models import AnswerFirstResult

_INSTRUCTIONS = """
Analyze the content for the ANSWER-FIRST LENS:

1. Identify all question-based headings (headings that end with "?" or are phrased as questions).
2. For each, check if a concise 40–60 word definition or direct answer immediately follows it.
3. List headers that are missing this direct answer as "missing_definitions".
4. Score from 1–10 (10 = every question header has a direct answer below it).

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
