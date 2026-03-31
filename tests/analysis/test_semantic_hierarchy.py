import json
from unittest.mock import patch

from lumina_geo.analysis.semantic_hierarchy import SemanticHierarchyLens
from lumina_geo.reporting.models import SemanticHierarchyResult

MOCK_RESPONSE = {
    "score": 6,
    "findings": ["H2 follows H1 logically"],
    "critical_fixes": ["Add missing H3 under Pricing"],
    "logic_breaks": ["'Contact Us' H2 under 'Technical Specs' H1"],
}


@patch("lumina_geo.analysis.base.call_gemini", return_value=json.dumps(MOCK_RESPONSE))
def test_semantic_hierarchy_lens_returns_result(mock_gemini):
    result = SemanticHierarchyLens().analyze("# Sample content")

    assert isinstance(result, SemanticHierarchyResult)
    assert result.score == 6
    assert len(result.logic_breaks) == 1
    mock_gemini.assert_called_once()
