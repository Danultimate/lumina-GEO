from unittest.mock import patch

from fastapi.testclient import TestClient

from api.main import app
from lumina_geo.ingestion.url_scraper import IngestionError
from lumina_geo.reporting.models import (
    AuditReport,
    AnswerFirstResult,
    GroundingResult,
    SemanticHierarchyResult,
)

client = TestClient(app)

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


@patch("api.routes.audit.build_report", return_value=MOCK_REPORT)
@patch("api.routes.audit.write_report")
def test_audit_endpoint_success(mock_write, mock_build):
    response = client.post("/audit", json={"target": "https://example.com"})

    assert response.status_code == 200
    data = response.json()
    assert data["composite_score"] == 7.67
    mock_build.assert_called_once_with("https://example.com")


@patch("api.routes.audit.build_report", side_effect=IngestionError("empty content"))
def test_audit_endpoint_ingestion_error(mock_build):
    response = client.post("/audit", json={"target": "https://bad.example.com"})

    assert response.status_code == 422
    assert "empty content" in response.json()["detail"]


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
