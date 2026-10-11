from __future__ import annotations

import re
from typing import Iterable

from app.models.schemas import Chunk


def _normalize_whitespace(text: str) -> str:
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'\s{2,}', ' ', text)
    return text.strip()


def chunk_text(
    text: str,
    document_id: str,
    file_name: str,
    page_number: int | None = None,
    chunk_size: int = 400,
    chunk_overlap: int = 80,
) -> list[Chunk]:
    cleaned = _normalize_whitespace(text)
    if not cleaned:
        return []

    sentences = re.split(r'(?<=[.!?])\s+', cleaned)
    chunks: list[Chunk] = []
    current = ''
    index = 0

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        if current and len(current) + len(sentence) > chunk_size:
            chunks.append(
                Chunk(
                    document_id=document_id,
                    file_name=file_name,
                    page_number=page_number,
                    chunk_index=index,
                    text=_normalize_whitespace(current),
                )
            )
            index += 1
            current = sentence
        else:
            if current:
                current = f'{current} {sentence}'
            else:
                current = sentence

        if len(current) > chunk_size:
            parts = re.split(r'(?<=[;:])\s+|\s+', current)
            words: list[str] = []
            for part in parts:
                if not part:
                    continue
                words.append(part)
            current_words = []
            accumulator = ''
            for word in words:
                candidate = f'{accumulator} {word}'.strip()
                if len(candidate) > chunk_size:
                    if accumulator:
                        chunks.append(
                            Chunk(
                                document_id=document_id,
                                file_name=file_name,
                                page_number=page_number,
                                chunk_index=index,
                                text=_normalize_whitespace(accumulator),
                            )
                        )
                        index += 1
                        accumulator = word
                    else:
                        accumulator = word
                else:
                    accumulator = candidate
            if accumulator:
                current = accumulator

    if current.strip():
        chunks.append(
            Chunk(
                document_id=document_id,
                file_name=file_name,
                page_number=page_number,
                chunk_index=index,
                text=_normalize_whitespace(current),
            )
        )

    if chunk_overlap > 0 and len(chunks) > 1:
        merged: list[Chunk] = []
        for i, chunk in enumerate(chunks):
            if i == 0:
                merged.append(chunk)
                continue
            previous = merged[-1]
            if len(previous.text.split()) < chunk_overlap:
                previous.text = _normalize_whitespace(f'{previous.text} {chunk.text}')
            else:
                merged.append(chunk)
        chunks = merged

    return [chunk for chunk in chunks if chunk.text]
