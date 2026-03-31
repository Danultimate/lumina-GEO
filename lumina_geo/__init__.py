from datetime import datetime, timezone

from lumina_geo.analysis.answer_first import AnswerFirstLens
from lumina_geo.analysis.grounding import GroundingLens
from lumina_geo.analysis.semantic_hierarchy import SemanticHierarchyLens
from lumina_geo.ingestion.repo_loader import load_repo
from lumina_geo.ingestion.url_scraper import scrape_url
from lumina_geo.reporting.models import AuditReport


def build_report(target: str) -> AuditReport:
    content = scrape_url(target) if target.startswith("http") else load_repo(target)

    grounding = GroundingLens().analyze(content)
    semantic = SemanticHierarchyLens().analyze(content)
    answer = AnswerFirstLens().analyze(content)

    composite = round((grounding.score + semantic.score + answer.score) / 3, 2)

    return AuditReport(
        url_or_path=target,
        composite_score=composite,
        grounding=grounding,
        semantic_hierarchy=semantic,
        answer_first=answer,
        generated_at=datetime.now(timezone.utc).isoformat(),
    )
