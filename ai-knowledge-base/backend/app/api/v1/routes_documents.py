from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, UploadFile
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_embedding_service
from app.db.models import Chunk, Document
from app.db.session import get_db_session
from app.providers.embeddings import EmbeddingProvider
from app.services.ingestion import ingest_document

router = APIRouter(prefix="/v1/documents", tags=["documents"])


class DocumentCreateResponse(BaseModel):
    doc_id: UUID
    status: str
    chunks: int


class DocumentItem(BaseModel):
    id: UUID
    title: str | None
    filename: str
    content_type: str


class DocumentDetail(DocumentItem):
    chunks: int


@router.post("", response_model=DocumentCreateResponse)
async def upload_document(
    title: str | None = Form(default=None),
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_db_session),
    embedding_provider: EmbeddingProvider = Depends(get_embedding_service),
) -> DocumentCreateResponse:
    doc_id, chunk_count = await ingest_document(session, file, embedding_provider, title=title)
    return DocumentCreateResponse(doc_id=doc_id, status="indexed", chunks=chunk_count)


@router.get("", response_model=list[DocumentItem])
async def list_documents(
    page: int = 1,
    page_size: int = 20,
    session: AsyncSession = Depends(get_db_session),
) -> list[DocumentItem]:
    offset = max(page - 1, 0) * page_size
    result = await session.execute(select(Document).order_by(Document.created_at.desc()).offset(offset).limit(page_size))
    docs = result.scalars().all()
    return [
        DocumentItem(id=doc.id, title=doc.title, filename=doc.filename, content_type=doc.content_type)
        for doc in docs
    ]


@router.get("/{doc_id}", response_model=DocumentDetail)
async def get_document(doc_id: UUID, session: AsyncSession = Depends(get_db_session)) -> DocumentDetail:
    doc = await session.scalar(select(Document).where(Document.id == doc_id))
    count = await session.scalar(select(func.count(Chunk.id)).where(Chunk.document_id == doc_id))
    if not doc:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Document not found")
    return DocumentDetail(
        id=doc.id,
        title=doc.title,
        filename=doc.filename,
        content_type=doc.content_type,
        chunks=int(count or 0),
    )
