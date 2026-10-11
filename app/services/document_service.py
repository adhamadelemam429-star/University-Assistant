from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from app.config import settings
from app.core.document_loader import extract_text_from_file
from app.core.text_chunker import chunk_text
from app.database.repositories import document_repository
from app.models.schemas import Chunk


class DocumentService:
    def __init__(self):
        self.repository = document_repository
        self._sample_documents_initialized = False

    def ensure_sample_documents_ingested(self) -> None:
        if self._sample_documents_initialized:
            return

        sample_dir = Path(settings.data_dir) / 'sample_documents'
        sample_files = sorted(
            path for path in sample_dir.iterdir()
            if path.is_file() and path.suffix.lower() in settings.allowed_extensions
        ) if sample_dir.exists() else []
        sample_names = {path.name for path in sample_files}
        legacy_names = {'admission_policy.txt', 'tuition_fees.txt', 'attendance_policy.txt', 'student_services.txt'}

        for document in self.get_documents():
            if document.get('file_name') in legacy_names:
                self.delete_document(document['document_id'])

        existing_names = {
            document.get('file_name')
            for document in self.get_documents()
            if document.get('file_name') in sample_names
        }
        for file_path in sample_files:
            if file_path.name not in existing_names:
                self.ingest_document(file_path)

        self._sample_documents_initialized = True

    def ingest_document(self, file_path: str | Path) -> dict:
        extracted = extract_text_from_file(file_path)
        document_id = str(uuid4())
        file_name = Path(file_path).name

        chunks = chunk_text(
            text=extracted.text,
            document_id=document_id,
            file_name=file_name,
            page_number=extracted.page_number,
            chunk_size=400,
            chunk_overlap=80,
        )

        metadata = {
            'document_id': document_id,
            'file_name': file_name,
            'page_number': extracted.page_number,
            'is_empty': extracted.is_empty,
            'warning': extracted.warning,
            'text_length': len(extracted.text),
            'chunk_count': len(chunks),
        }
        self.repository.save_document(metadata)

        for index, chunk in enumerate(chunks):
            chunk_record = {
                'chunk_id': f'{document_id}-{index}',
                'document_id': document_id,
                'file_name': chunk.file_name,
                'page_number': chunk.page_number,
                'chunk_index': index,
                'text': chunk.text,
            }
            self.repository.save_chunk(chunk_record)

        return metadata

    def get_documents(self) -> list[dict]:
        return self.repository.list_documents()

    def delete_document(self, document_id: str) -> bool:
        return self.repository.delete_document(document_id)


document_service = DocumentService()
