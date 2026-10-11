from __future__ import annotations

import re

from app.config import settings
from app.core.embeddings import cosine_similarity, generate_embedding
from app.models.schemas import Chunk


STOP_WORDS = {
    'the', 'a', 'an', 'and', 'or', 'of', 'for', 'to', 'in', 'on', 'at', 'is', 'are',
    'what', 'when', 'where', 'why', 'how', 'with', 'from', 'about', 'this', 'that',
    'it', 'its', 'be', 'by', 'as', 'if', 'then', 'which', 'who', 'whom', 'your', 'our',
    'their', 'there', 'will', 'should', 'must', 'can', 'could', 'may', 'into', 'over',
    'under', 'after', 'before', 'during', 'between', 'among', 'ما', 'هي', 'هل', 'من',
    'في', 'عن', 'على', 'كم', 'ماذا'
}

ARABIC_TERM_MAP = {
    'الاوراق': ('documents',),
    'ورق': ('documents',),
    'الورق': ('documents',),
    'مستندات': ('documents',),
    'المستندات': ('documents',),
    'مطلوبة': ('required',),
    'المطلوبة': ('required',),
    'المطلوب': ('required',),
    'للتقديم': ('admission', 'application'),
    'التقديم': ('admission', 'application'),
    'اقدم': ('admission', 'application'),
    'القبول': ('admission', 'applicants'),
    'رسوم': ('fees',),
    'الرسوم': ('fees',),
    'مصاريف': ('fees',),
    'المصاريف': ('fees',),
    'حضور': ('attendance',),
    'الحضور': ('attendance',),
    'غياب': ('attendance',),
    'الاختبارات': ('examinations', 'exams'),
    'الامتحانات': ('examinations', 'exams'),
    'الكشف': ('medical', 'examination'),
    'الطبي': ('medical',),
    'الوافدين': ('international', 'students'),
    'وافد': ('international', 'student'),
    'الكليات': ('faculties', 'colleges'),
    'كلية': ('faculty', 'college'),
    'كليات': ('faculties', 'colleges'),
    'البرامج': ('programs',),
    'الجامعية': ('undergraduate', 'university'),
    'الخدمات': ('services',),
    'الطلاب': ('students',),
    'الطالب': ('student',),
    'السكن': ('housing', 'residence'),
    'المدينة': ('housing', 'residence'),
    'الجامعي': ('housing', 'university'),
    'الجامعيه': ('housing', 'university'),
    'جامعية': ('university',),
    'الجامعية': ('university', 'housing'),
    'النتائج': ('results',),
    'الجداول': ('schedules',),
    'المنح': ('scholarships',),
}


def _tokenize(text: str) -> set[str]:
    terms: set[str] = set()
    for token in re.findall(r"\w+", text):
        normalized = re.sub(r'[\u064b-\u065f\u0670\u0640]', '', token.lower())
        normalized = normalized.translate(str.maketrans({'أ': 'ا', 'إ': 'ا', 'آ': 'ا', 'ى': 'ي'}))
        if normalized in STOP_WORDS or len(normalized) <= 1:
            continue
        terms.add(normalized)
        terms.update(ARABIC_TERM_MAP.get(normalized, (normalized,)))
    return terms


def _is_tuition_question(query: str) -> bool:
    normalized = re.sub(r'[\u064b-\u065f\u0670\u0640]', '', query.lower())
    has_fee_term = re.search(r'رسوم|مصاريف|مصروفات|fees?', normalized)
    asks_about_housing = re.search(r'سكن|اقامة|مدينة جامعية|housing|residen', normalized)
    return 'tuition' in normalized or bool(has_fee_term and not asks_about_housing)


def _has_tuition_context(text: str) -> bool:
    normalized = re.sub(r'[\u064b-\u065f\u0670\u0640]', '', text.lower())
    normalized = normalized.translate(str.maketrans({'أ': 'ا', 'إ': 'ا', 'آ': 'ا', 'ى': 'ي'}))
    if re.search(r'\btuition\b', normalized):
        return True
    return bool(
        re.search(r'(رسوم|مصاريف|مصروفات)\s+(الدراسة|دراسية|التعليم|تعليمية)', normalized)
        or re.search(r'(الدراسة|دراسية|التعليم|تعليمية)\s+(رسوم|مصاريف|مصروفات)', normalized)
    )


def retrieve_relevant_chunks(query: str, chunks: list[Chunk], top_k: int | None = None, min_score: float | None = None) -> list[Chunk]:
    if not chunks:
        return []

    top_k = top_k or settings.max_retrieved_chunks
    min_score = min_score if min_score is not None else settings.min_relevance_score
    query_terms = _tokenize(query)
    if not query_terms:
        return []
    tuition_question = _is_tuition_question(query)

    scored: list[tuple[Chunk, float]] = []
    for chunk in chunks:
        chunk_text = chunk.text or ''
        if tuition_question and not _has_tuition_context(chunk_text):
            continue
        chunk_terms = _tokenize(chunk_text)
        overlap = len(query_terms & chunk_terms) / max(len(query_terms), 1)
        if overlap < 0.4:
            continue

        embedding_score = cosine_similarity(generate_embedding(query), generate_embedding(chunk_text))
        score = overlap + (embedding_score * 0.5)
        if score < min_score:
            continue
        scored.append((chunk, float(score)))

    scored.sort(key=lambda item: item[1], reverse=True)
    return [chunk for chunk, _ in scored[:top_k]]
