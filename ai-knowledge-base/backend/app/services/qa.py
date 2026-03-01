from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Document, Question
from app.providers.embeddings import EmbeddingProvider
from app.providers.llm import LLMProvider
from app.services.retrieval import search_chunks


async def answer_question(
    session: AsyncSession,
    doc_id: UUID,
    question: str,
    top_k: int,
    embedding_provider: EmbeddingProvider,
    llm_provider: LLMProvider,
) -> tuple[str, list[dict]]:
    document = await session.scalar(select(Document).where(Document.id == doc_id))
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    query_embedding = (await embedding_provider.embed_texts([question]))[0]
    results = await search_chunks(session=session, document_id=doc_id, query_embedding=query_embedding, top_k=top_k)

    context = "\n\n".join(item["text"] for item in results)
    answer = await llm_provider.answer(question=question, context=context)

    session.add(Question(document_id=doc_id, question=question, answer=answer))
    await session.commit()

    sources = [
        {
            "id": str(item["id"]),
            "score": float(item["score"]),
            "text_snippet": item["text"][:300],
            "chunk_index": item["chunk_index"],
        }
        for item in results
    ]
    return answer, sources
