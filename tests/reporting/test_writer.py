import json

from lumina_geo.reporting.models import (
    AuditReport,
    AnswerFirstResult,
    GroundingResult,
    SemanticHierarchyResult,
)
from lumina_geo.reporting.writer import write_report


def _make_report() -> AuditReport:
    return AuditReport(
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


def test_write_report_creates_json(tmp_path):
    report = _make_report()
    write_report(report, str(tmp_path))

    json_file = tmp_path / "report.json"
    assert json_file.exists()

    data = json.loads(json_file.read_text())
    assert data["composite_score"] == 7.67
    assert data["url_or_path"] == "https://example.com"


def test_write_report_creates_markdown(tmp_path):
    report = _make_report()
    write_report(report, str(tmp_path))

    md_file = tmp_path / "report.md"
    assert md_file.exists()

    content = md_file.read_text()
    assert "Lumina-GEO Audit Report" in content
    assert "7.7 / 10" in content


def test_write_report_creates_output_dir(tmp_path):
    report = _make_report()
    nested = tmp_path / "a" / "b" / "c"

    write_report(report, str(nested))

    assert (nested / "report.json").exists()
