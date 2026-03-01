from __future__ import annotations

from abc import ABC, abstractmethod

from openai import AsyncOpenAI

from app.core.config import get_settings


class LLMProvider(ABC):
    @abstractmethod
    async def answer(self, question: str, context: str) -> str:
        raise NotImplementedError


class StubLLMProvider(LLMProvider):
    async def answer(self, question: str, context: str) -> str:
        excerpt = context[:500] if context else "Nenhum contexto recuperado."
        return f"Best-effort answer para: '{question}'. Contexto relevante: {excerpt}"


class OpenAILLMProvider(LLMProvider):
    def __init__(self, api_key: str, model: str) -> None:
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model

    async def answer(self, question: str, context: str) -> str:
        prompt = (
            "Você é um assistente de Q&A sobre documentos. "
            "Responda somente com base no contexto."
        )
        completion = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": prompt},
                {
                    "role": "user",
                    "content": f"Pergunta: {question}\n\nContexto:\n{context}",
                },
            ],
            temperature=0.0,
        )
        return completion.choices[0].message.content or "Sem resposta."


def get_llm_provider() -> LLMProvider:
    settings = get_settings()
    if settings.openai_api_key:
        return OpenAILLMProvider(settings.openai_api_key, settings.openai_chat_model)
    return StubLLMProvider()
