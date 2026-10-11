from __future__ import annotations

from app.config import settings


class LLMProvider:
    def __init__(self):
        self.provider = settings.llm_provider.lower()
        self.api_key = settings.llm_api_key
        self.model = settings.llm_model or 'demo-model'

    def is_available(self) -> bool:
        return self.provider not in {'', 'demo'} and bool(self.api_key)

    def generate(self, question: str, context: str) -> str | None:
        if not self.is_available():
            return None
        if self.provider == 'openai':
            return f"OpenAI answer for: {question} based on context:\n{context[:400]}"
        return f"LLM answer generated for: {question} using {self.provider}."
