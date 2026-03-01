from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_embedding_service, get_llm_service
from app.db.session import get_db_session
from app.providers.embeddings import EmbeddingProvider
from app.providers.llm import LLMProvider
from app.services.qa import answer_question

router = APIRouter(prefix="/v1/qa", tags=["qa"])


class QARequest(BaseModel):
    doc_id: UUID
    question: str = Field(min_length=3)
    top_k: int = Field(default=5, ge=1, le=20)


class QASource(BaseModel):
    id: str
    score: float
    text_snippet: str
    chunk_index: int


class QAResponse(BaseModel):
    answer: str
    sources: list[QASource]


@router.post("", response_model=QAResponse)
async def qa_endpoint(
    payload: QARequest,
    session: AsyncSession = Depends(get_db_session),
    embedding_provider: EmbeddingProvider = Depends(get_embedding_service),
    llm_provider: LLMProvider = Depends(get_llm_service),
) -> QAResponse:
    answer, sources = await answer_question(
        session,
        doc_id=payload.doc_id,
        question=payload.question,
        top_k=payload.top_k,
        embedding_provider=embedding_provider,
        llm_provider=llm_provider,
    )
    return QAResponse(answer=answer, sources=[QASource(**item) for item in sources])
