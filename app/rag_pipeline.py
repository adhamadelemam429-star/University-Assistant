from __future__ import annotations

from app.config import settings
from app.core.llm_provider import LLMProvider
from app.core.retriever import retrieve_relevant_chunks
from app.models.schemas import Chunk, RAGAnswer, SourceReference


class RAGPipeline:
    def __init__(self, llm_provider: LLMProvider | None = None):
        self.llm_provider = llm_provider or LLMProvider()

    @staticmethod
    def _clean_question(question: str) -> str:
        return ' '.join(question.strip().split())

    @staticmethod
    def _question_is_arabic(question: str) -> bool:
        return any('\u0600' <= character <= '\u06ff' for character in question)

    def answer_question(self, question: str, chunks: list[Chunk], llm_enabled: bool = False) -> RAGAnswer:
        cleaned_question = self._clean_question(question)
        answer_in_arabic = self._question_is_arabic(cleaned_question)
        if not cleaned_question:
            message = 'من فضلك اكتب سؤالًا واضحًا عن مستندات الجامعة.' if answer_in_arabic else 'Please provide a clear question about the university documents.'
            return RAGAnswer(answer=message, sources=[])

        relevant = retrieve_relevant_chunks(
            query=cleaned_question,
            chunks=chunks,
            top_k=settings.max_retrieved_chunks,
            min_score=settings.min_relevance_score,
        )

        language_suffix = '_ar.txt' if answer_in_arabic else '_en.txt'
        language_specific = [chunk for chunk in relevant if chunk.file_name.lower().endswith(language_suffix)]
        if language_specific:
            relevant = language_specific

        if relevant:
            file_counts: dict[str, int] = {}
            for chunk in relevant:
                file_counts[chunk.file_name] = file_counts.get(chunk.file_name, 0) + 1
            best_file = max(file_counts, key=file_counts.get)
            relevant = [chunk for chunk in relevant if chunk.file_name == best_file]

        if not relevant:
            message = (
                'لا توجد معلومات كافية في المستندات المتاحة للإجابة عن هذا السؤال بشكل موثوق.'
                if answer_in_arabic
                else 'There is not enough evidence in the available documents to answer this question reliably.'
            )
            return RAGAnswer(answer=message, sources=[])

        sources = []
        seen_sources: set[tuple[str, str, int | None]] = set()
        for chunk in relevant:
            source_key = (chunk.document_id, chunk.file_name, chunk.page_number)
            if source_key not in seen_sources:
                seen_sources.add(source_key)
                sources.append(SourceReference(document_id=chunk.document_id, file_name=chunk.file_name, page_number=chunk.page_number))

        if llm_enabled and self.llm_provider.is_available():
            context = '\n\n'.join(chunk.text for chunk in relevant)
            llm_answer = self.llm_provider.generate(cleaned_question, context)
            if llm_answer:
                return RAGAnswer(answer=llm_answer, sources=sources, used_chunks=relevant)

        reference_texts = []
        for chunk in relevant:
            reference_texts.append(f"{chunk.file_name} (page {chunk.page_number if chunk.page_number else 'n/a'}): {chunk.text}")

        introduction = (
            'وفقًا للمستندات الرسمية المتاحة من جامعة القاهرة:\n\n'
            if answer_in_arabic
            else 'According to the available official Cairo University documents:\n\n'
        )
        answer_text = introduction + '\n\n'.join(reference_texts[:2])
        return RAGAnswer(answer=answer_text, sources=sources, used_chunks=relevant)
