from __future__ import annotations

from pathlib import Path
from uuid import UUID

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.models import Chunk, Document
from app.providers.embeddings import EmbeddingProvider
from app.services.chunking import chunk_text
from app.utils.files import build_document_path, sanitize_filename, validate_upload
from app.utils.text import extract_text_from_pdf, extract_text_from_txt


async def ingest_document(
    session: AsyncSession,
    file: UploadFile,
    embedding_provider: EmbeddingProvider,
    title: str | None = None,
) -> tuple[UUID, int]:
    settings = get_settings()
    validate_upload(file)
    content = await file.read()
    if len(content) > settings.max_upload_size_bytes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File too large")

    safe_name = sanitize_filename(file.filename or "document")
    document = Document(title=title, filename=safe_name, content_type=file.content_type or "application/octet-stream")
    session.add(document)
    await session.flush()

    path = build_document_path(document.id)
    path.parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_bytes(content)

    if document.content_type == "application/pdf":
        text = extract_text_from_pdf(content)
    else:
        text = extract_text_from_txt(content)

    chunks = chunk_text(text, settings.chunk_size, settings.chunk_overlap)
    if not chunks:
        chunks = [""]

    vectors = await embedding_provider.embed_texts(chunks)
    if len(vectors) != len(chunks):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Embedding failure")

    for i, (chunk, vector) in enumerate(zip(chunks, vectors, strict=True)):
        session.add(
            Chunk(
                document_id=document.id,
                chunk_index=i,
                text=chunk,
                embedding=vector,
                embedding_json=vector,
            )
        )

    await session.commit()
    return document.id, len(chunks)
