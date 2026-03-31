from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from api.routes.audit import router as audit_router

app = FastAPI(
    title="Lumina-GEO",
    description="Audit websites and code repositories for AI-Readability and GEO readiness.",
    version="0.1.0",
)

app.include_router(audit_router)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/")
def dashboard() -> FileResponse:
    return FileResponse("static/index.html")
