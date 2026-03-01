from __future__ import annotations

from app.providers.embeddings import EmbeddingProvider, get_embedding_provider
from app.providers.llm import LLMProvider, get_llm_provider


def get_embedding_service() -> EmbeddingProvider:
    return get_embedding_provider()


def get_llm_service() -> LLMProvider:
    return get_llm_provider()
