from app.core.text_chunker import chunk_text


def test_chunk_text_preserves_metadata_and_page_numbers():
    text = 'Admission policy paragraph one. ' * 20
    chunks = chunk_text(
        text,
        document_id='doc-1',
        file_name='admission_policy.pdf',
        page_number=3,
        chunk_size=80,
        chunk_overlap=20,
    )

    assert len(chunks) > 1
    assert all(chunk.document_id == 'doc-1' for chunk in chunks)
    assert all(chunk.file_name == 'admission_policy.pdf' for chunk in chunks)
    assert all(chunk.page_number == 3 for chunk in chunks)
    assert all(len(chunk.text) > 0 for chunk in chunks)
