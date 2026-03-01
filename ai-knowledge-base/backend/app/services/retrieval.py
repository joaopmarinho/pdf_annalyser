from __future__ import annotations

import math
from typing import Any
from uuid import UUID

from sqlalchemy import Select, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Chunk


def _cosine_distance(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b, strict=False))
    norm_a = math.sqrt(sum(x * x for x in a)) or 1.0
    norm_b = math.sqrt(sum(y * y for y in b)) or 1.0
    return 1.0 - (dot / (norm_a * norm_b))


async def search_chunks(
    session: AsyncSession, document_id: UUID, query_embedding: list[float], top_k: int
) -> list[dict[str, Any]]:
    dialect = session.bind.dialect.name if session.bind else ""
    if dialect == "postgresql":
        stmt = text(
            """
            SELECT id, chunk_index, text,
                   (embedding <=> CAST(:query_embedding AS vector)) AS score
            FROM chunks
            WHERE document_id = :document_id
            ORDER BY embedding <=> CAST(:query_embedding AS vector)
            LIMIT :top_k
            """
        )
        result = await session.execute(
            stmt,
            {
                "document_id": str(document_id),
                "query_embedding": str(query_embedding),
                "top_k": top_k,
            },
        )
        rows = result.mappings().all()
        return [dict(row) for row in rows]

    stmt_fallback: Select[tuple[Chunk]] = select(Chunk).where(Chunk.document_id == document_id)
    result_fallback = await session.execute(stmt_fallback)
    chunks = result_fallback.scalars().all()
    scored = [
        {
            "id": chunk.id,
            "chunk_index": chunk.chunk_index,
            "text": chunk.text,
            "score": _cosine_distance(query_embedding, chunk.embedding_json or []),
        }
        for chunk in chunks
    ]
    scored.sort(key=lambda row: row["score"])
    return scored[:top_k]
