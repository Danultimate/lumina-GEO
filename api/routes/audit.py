from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from lumina_geo import build_report
from lumina_geo.ingestion.url_scraper import IngestionError
from lumina_geo.reporting.models import AuditReport
from lumina_geo.reporting.writer import write_report

router = APIRouter()


class AuditRequest(BaseModel):
    target: str
    output_dir: str = "."


@router.post("/audit", response_model=AuditReport)
def audit(request: AuditRequest) -> AuditReport:
    try:
        report = build_report(request.target)
    except IngestionError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    write_report(report, request.output_dir)
    return report
