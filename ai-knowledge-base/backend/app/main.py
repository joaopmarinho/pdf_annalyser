from __future__ import annotations

from fastapi import FastAPI

from app.api.v1 import routes_documents, routes_qa, routes_questions
from app.core.config import get_settings
from app.core.logging import configure_logging

configure_logging()
settings = get_settings()

app = FastAPI(title=settings.app_name, version=settings.app_version)

app.include_router(routes_documents.router)
app.include_router(routes_qa.router)
app.include_router(routes_questions.router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "version": settings.app_version}
