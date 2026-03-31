import json

from lumina_geo.analysis.base import BaseLens
from lumina_geo.reporting.models import SemanticHierarchyResult

_INSTRUCTIONS = """
Analyze the content for the SEMANTIC HIERARCHY LENS:

1. Check if H1 through H4 tags follow a logical topical flow.
2. Identify "Logic Breaks": subheadings that do not support or relate to their parent heading.
3. Score the overall semantic structure from 1–10 (10 = perfect logical hierarchy).

Respond ONLY with this JSON structure:
{
  "score": <int 1-10>,
  "findings": [<string>, ...],
  "critical_fixes": [<string>, ...],
  "logic_breaks": [<string>, ...]
}
"""


class SemanticHierarchyLens(BaseLens):
    def analyze(self, content: str) -> SemanticHierarchyResult:
        raw = self._call(content, _INSTRUCTIONS)
        data = json.loads(raw)
        return SemanticHierarchyResult(**data)
