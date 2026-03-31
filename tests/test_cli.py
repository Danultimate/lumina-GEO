import json
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from cli import app
from lumina_geo.reporting.models import (
    AuditReport,
    AnswerFirstResult,
    GroundingResult,
    SemanticHierarchyResult,
)

runner = CliRunner()

MOCK_REPORT = AuditReport(
    url_or_path="https://example.com",
    composite_score=7.67,
    grounding=GroundingResult(
        score=8, findings=[], critical_fixes=[],
        schema_gaps=[], is_groundable=True, citation_probability=7,
    ),
    semantic_hierarchy=SemanticHierarchyResult(
        score=7, findings=[], critical_fixes=[], logic_breaks=[],
    ),
    answer_first=AnswerFirstResult(
        score=8, findings=[], critical_fixes=[], missing_definitions=[],
    ),
    generated_at="2026-03-31T00:00:00+00:00",
)


@patch("cli.build_report", return_value=MOCK_REPORT)
@patch("cli.write_report")
def test_cli_audit_url(mock_write, mock_build, tmp_path):
    result = runner.invoke(app, ["audit", "https://example.com", "--output-dir", str(tmp_path)])

    assert result.exit_code == 0
    assert "7.7 / 10" in result.output
    mock_build.assert_called_once_with("https://example.com")
    mock_write.assert_called_once()


@patch("cli.build_report", return_value=MOCK_REPORT)
@patch("cli.write_report")
def test_cli_audit_repo(mock_write, mock_build, tmp_path):
    result = runner.invoke(app, ["audit", "/some/repo", "--output-dir", str(tmp_path)])

    assert result.exit_code == 0
    mock_build.assert_called_once_with("/some/repo")
