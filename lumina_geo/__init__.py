from datetime import datetime, timezone

from lumina_geo.analysis.answer_first import AnswerFirstLens
from lumina_geo.analysis.authority import AuthorityLens
from lumina_geo.analysis.grounding import GroundingLens
from lumina_geo.analysis.robots_check import check_robots
from lumina_geo.analysis.semantic_hierarchy import SemanticHierarchyLens
from lumina_geo.ingestion.repo_loader import load_repo
from lumina_geo.ingestion.url_scraper import scrape_url
from lumina_geo.reporting.models import AuditReport, PlatformScores


def _calc_platform_scores(grounding, semantic, answer, authority, ai_access) -> PlatformScores:
    # Google AI Overviews weights: schema/grounding heavy, structure secondary
    google = round(
        grounding.score * 0.35 + semantic.score * 0.30 +
        answer.score * 0.20 + authority.score * 0.15,
        2,
    )
    # ChatGPT / Perplexity weights: authority heavy, answer-first secondary
    chatgpt = round(
        authority.score * 0.35 + answer.score * 0.25 +
        grounding.score * 0.25 + semantic.score * 0.15,
        2,
    )
    # Cap platform scores if AI bots are blocked
    if ai_access.critical:
        google = min(google, 3.0)
        chatgpt = min(chatgpt, 3.0)

    return PlatformScores(
        google_ai_overviews=google,
        chatgpt_perplexity=chatgpt,
    )


def build_report(target: str) -> AuditReport:
    content = scrape_url(target) if target.startswith("http") else load_repo(target)

    grounding = GroundingLens().analyze(content)
    semantic = SemanticHierarchyLens().analyze(content)
    answer = AnswerFirstLens().analyze(content)
    authority = AuthorityLens().analyze(content)
    ai_access = check_robots(target)

    composite = round(
        (grounding.score + semantic.score + answer.score + authority.score) / 4, 2
    )
    platform = _calc_platform_scores(grounding, semantic, answer, authority, ai_access)

    return AuditReport(
        url_or_path=target,
        composite_score=composite,
        platform_scores=platform,
        grounding=grounding,
        semantic_hierarchy=semantic,
        answer_first=answer,
        authority=authority,
        ai_access=ai_access,
        generated_at=datetime.now(timezone.utc).isoformat(),
    )
