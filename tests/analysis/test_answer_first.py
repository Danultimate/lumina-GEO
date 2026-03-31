import json
from unittest.mock import patch

from lumina_geo.analysis.answer_first import AnswerFirstLens
from lumina_geo.reporting.models import AnswerFirstResult

MOCK_RESPONSE = {
    "score": 9,
    "findings": ["All question headers have direct answers"],
    "critical_fixes": [],
    "missing_definitions": [],
}


@patch("lumina_geo.analysis.base.call_gemini", return_value=json.dumps(MOCK_RESPONSE))
def test_answer_first_lens_returns_result(mock_gemini):
    result = AnswerFirstLens().analyze("# Sample content")

    assert isinstance(result, AnswerFirstResult)
    assert result.score == 9
    assert result.missing_definitions == []
    mock_gemini.assert_called_once()
