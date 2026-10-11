from pathlib import Path

from app.core.document_loader import extract_text_from_file


def test_extract_text_from_text_file(tmp_path):
    file_path = tmp_path / 'admission.txt'
    file_path.write_text('Admission requirements\n\n- High school diploma\n- Passport copy\n', encoding='utf-8')

    result = extract_text_from_file(file_path)

    assert 'Admission requirements' in result.text
    assert result.file_name == 'admission.txt'
    assert result.page_number is None


def test_extract_text_from_empty_file(tmp_path):
    file_path = tmp_path / 'empty.txt'
    file_path.write_text('', encoding='utf-8')

    result = extract_text_from_file(file_path)

    assert result.text == ''
    assert result.is_empty is True
