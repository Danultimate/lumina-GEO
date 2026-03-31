import json
from unittest.mock import patch

from lumina_geo.analysis.grounding import GroundingLens
from lumina_geo.reporting.models import GroundingResult

MOCK_RESPONSE = {
    "score": 8,
    "citation_probability": 7,
    "is_groundable": True,
    "findings": ["JSON-LD present", "Prices in table"],
    "critical_fixes": [],
    "schema_gaps": ["Missing Review schema"],
}


@patch("lumina_geo.analysis.base.call_gemini", return_value=json.dumps(MOCK_RESPONSE))
def test_grounding_lens_returns_result(mock_gemini):
    result = GroundingLens().analyze("# Sample content")

    assert isinstance(result, GroundingResult)
    assert result.score == 8
    assert result.citation_probability == 7
    assert result.is_groundable is True
    assert "Missing Review schema" in result.schema_gaps
    mock_gemini.assert_called_once()
