from app.core.text_chunker import chunk_text
from app.core.retriever import retrieve_relevant_chunks


def test_retrieve_relevant_chunks_for_question():
    chunks = [
        chunk_text('Tuition fees are 12000 SAR per year for undergraduate students.', document_id='doc-1', file_name='fees.txt', page_number=1)[0],
        chunk_text('Attendance policy requires at least 75 percent attendance.', document_id='doc-1', file_name='fees.txt', page_number=2)[0],
    ]

    results = retrieve_relevant_chunks(
        query='What are tuition fees?',
        chunks=chunks,
        top_k=1,
        min_score=0.0,
    )

    assert len(results) == 1
    assert 'fee' in results[0].text.lower() or 'tuition' in results[0].text.lower()


def test_retrieve_english_admission_document_for_arabic_question():
    chunk = chunk_text(
        'Required documents for admission include a completed application form and a high school transcript.',
        document_id='admission',
        file_name='admission_policy.txt',
        page_number=None,
    )[0]

    results = retrieve_relevant_chunks('ما الأوراق المطلوبة للتقديم؟', [chunk], min_score=0.0)

    assert results == [chunk]
