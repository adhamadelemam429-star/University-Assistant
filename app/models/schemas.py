from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class SourceReference:
    document_id: str
    file_name: str
    page_number: Optional[int] = None


@dataclass
class Chunk:
    document_id: str
    file_name: str
    page_number: Optional[int]
    chunk_index: int
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ExtractedDocument:
    file_name: str
    text: str
    page_number: Optional[int] = None
    is_empty: bool = False
    is_scanned_pdf: bool = False
    warning: Optional[str] = None


@dataclass
class RAGAnswer:
    answer: str
    sources: list[SourceReference]
    used_chunks: list[Chunk] = field(default_factory=list)


@dataclass
class ChatMessage:
    role: str
    content: str


class ChatRequest:
    def __init__(self, question: str):
        self.question = question


class ChatResponse:
    def __init__(self, answer: str, sources: list[dict[str, Any]] | None = None):
        self.answer = answer
        self.sources = sources or []
