from __future__ import annotations

import hashlib
import math
from abc import ABC, abstractmethod

from openai import AsyncOpenAI

from app.core.config import get_settings


class EmbeddingProvider(ABC):
    @abstractmethod
    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError


class HashEmbeddingProvider(EmbeddingProvider):
    def __init__(self, dim: int) -> None:
        self.dim = dim

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        vectors: list[list[float]] = []
        for text in texts:
            buckets = [0.0] * self.dim
            tokens = text.lower().split()
            for token in tokens:
                digest = hashlib.sha256(token.encode("utf-8")).digest()
                index = int.from_bytes(digest[:4], "big") % self.dim
                sign = 1.0 if digest[4] % 2 == 0 else -1.0
                buckets[index] += sign
            norm = math.sqrt(sum(v * v for v in buckets)) or 1.0
            vectors.append([v / norm for v in buckets])
        return vectors


class OpenAIEmbeddingProvider(EmbeddingProvider):
    def __init__(self, api_key: str, model: str) -> None:
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        response = await self.client.embeddings.create(model=self.model, input=texts)
        return [item.embedding for item in response.data]


def get_embedding_provider() -> EmbeddingProvider:
    settings = get_settings()
    if settings.openai_api_key:
        return OpenAIEmbeddingProvider(settings.openai_api_key, settings.openai_embedding_model)
    return HashEmbeddingProvider(settings.embedding_dim)
