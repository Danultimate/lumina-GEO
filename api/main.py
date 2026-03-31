from fastapi import FastAPI

from api.routes.audit import router as audit_router

app = FastAPI(
    title="Lumina-GEO",
    description="Audit websites and code repositories for AI-Readability and GEO readiness.",
    version="0.1.0",
)

app.include_router(audit_router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
