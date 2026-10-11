from app.core.text_chunker import chunk_text
from app.rag_pipeline import RAGPipeline


def test_rag_returns_no_answer_when_no_evidence_found():
    pipeline = RAGPipeline()
    chunks = [
        chunk_text('The university uses a standard academic schedule.', document_id='doc-1', file_name='schedule.txt', page_number=1)[0]
    ]

    answer = pipeline.answer_question(
        question='What are the tuition fees?',
        chunks=chunks,
        llm_enabled=False,
    )

    assert 'not enough evidence' in answer.answer.lower() or 'not available' in answer.answer.lower()
    assert answer.sources == []


def test_arabic_question_without_matching_evidence_gets_arabic_fallback():
    pipeline = RAGPipeline()
    chunks = [
        chunk_text(
            'رسوم الإقامة بالمدينة الجامعية يحددها المجلس الأعلى للجامعات.',
            document_id='doc-1',
            file_name='cairo_housing_ar.txt',
            page_number=None,
        )[0]
    ]

    answer = pipeline.answer_question('ما رسوم الدراسة؟', chunks, llm_enabled=False)

    assert 'لا توجد معلومات كافية' in answer.answer
    assert answer.sources == []


def test_arabic_question_is_answered_from_arabic_evidence():
    pipeline = RAGPipeline()
    chunk = chunk_text(
        'الأوراق المطلوبة للتقديم تشمل شهادة الثانوية العامة وشهادة الميلاد المميكنة.',
        document_id='admission-ar',
        file_name='cairo_admission_ar.txt',
        page_number=None,
    )[0]

    answer = pipeline.answer_question('ما الأوراق المطلوبة للتقديم؟', [chunk], llm_enabled=False)

    assert answer.answer.startswith('وفقًا للمستندات الرسمية المتاحة من جامعة القاهرة:')
    assert 'شهادة الثانوية العامة' in answer.answer
    assert [source.file_name for source in answer.sources] == ['cairo_admission_ar.txt']
