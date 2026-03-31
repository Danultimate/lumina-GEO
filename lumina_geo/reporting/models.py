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


class AuditReport(BaseModel):
    url_or_path: str
    composite_score: float
    grounding: GroundingResult
    semantic_hierarchy: SemanticHierarchyResult
    answer_first: AnswerFirstResult
    generated_at: str
