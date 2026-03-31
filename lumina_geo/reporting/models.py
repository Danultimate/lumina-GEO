from typing import List

from pydantic import BaseModel, Field


class LensResult(BaseModel):
    score: int = Field(..., ge=1, le=10)
    findings: List[str]
    critical_fixes: List[str]


class GroundingResult(LensResult):
    schema_gaps: List[str]
    is_groundable: bool
    citation_probability: int = Field(..., ge=1, le=10)


class SemanticHierarchyResult(LensResult):
    logic_breaks: List[str]


class AnswerFirstResult(LensResult):
    missing_definitions: List[str]


class AuthorityResult(LensResult):
    has_named_author: bool
    has_statistics: bool
    has_expert_quotes: bool
    has_date_signals: bool
    has_external_citations: bool
    authority_signals: List[str]


class AIAccessResult(BaseModel):
    checked: bool
    blocked_bots: List[str]
    all_bots_allowed: bool
    critical: bool
    fixes: List[str]


class PlatformScores(BaseModel):
    google_ai_overviews: float
    chatgpt_perplexity: float


class AuditReport(BaseModel):
    url_or_path: str
    composite_score: float
    platform_scores: PlatformScores
    grounding: GroundingResult
    semantic_hierarchy: SemanticHierarchyResult
    answer_first: AnswerFirstResult
    authority: AuthorityResult
    ai_access: AIAccessResult
    generated_at: str
