from __future__ import annotations

import re
from pathlib import Path
from uuid import UUID

from fastapi import HTTPException, UploadFile, status

from app.core.config import get_settings

FILENAME_RE = re.compile(r"[^a-zA-Z0-9._-]+")


def sanitize_filename(filename: str) -> str:
    cleaned = FILENAME_RE.sub("_", filename).strip("._")
    return cleaned or "document"


def validate_upload(file: UploadFile) -> None:
    settings = get_settings()
    if file.content_type not in settings.allowed_content_types:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported content type")


def build_document_path(doc_id: UUID) -> Path:
    settings = get_settings()
    return settings.upload_dir / str(doc_id) / "original"
