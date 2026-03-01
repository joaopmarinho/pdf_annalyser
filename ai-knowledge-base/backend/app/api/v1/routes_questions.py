from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Question
from app.db.session import get_db_session

router = APIRouter(prefix="/v1/questions", tags=["questions"])


class QuestionItem(BaseModel):
    id: UUID
    document_id: UUID
    question: str
    answer: str


@router.get("", response_model=list[QuestionItem])
async def list_questions(
    doc_id: UUID | None = None,
    page: int = 1,
    page_size: int = 20,
    session: AsyncSession = Depends(get_db_session),
) -> list[QuestionItem]:
    stmt = select(Question).order_by(Question.created_at.desc())
    if doc_id:
        stmt = stmt.where(Question.document_id == doc_id)
    stmt = stmt.offset(max(page - 1, 0) * page_size).limit(page_size)
    result = await session.execute(stmt)
    rows = result.scalars().all()
    return [
        QuestionItem(id=q.id, document_id=q.document_id, question=q.question, answer=q.answer)
        for q in rows
    ]
