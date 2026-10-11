from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from pydantic import BaseModel

from app.config import settings
from app.services.chat_service import chat_service
from app.services.document_service import document_service

router = APIRouter()


class ChatRequestModel(BaseModel):
    question: str


class ChatResponseModel(BaseModel):
    answer: str
    sources: list[dict]


@router.get('/health')
def health_check() -> dict:
    return {'status': 'ok', 'app': settings.app_name, 'environment': settings.app_env}


@router.post('/chat', response_model=ChatResponseModel)
def chat(request: ChatRequestModel) -> dict:
    if not request.question or not request.question.strip():
        raise HTTPException(status_code=400, detail='A valid question is required.')
    return chat_service.answer_question(request.question)


@router.post('/documents/upload')
def upload_document(file: UploadFile = File(...)) -> dict:
    allowed = {ext.lower() for ext in settings.allowed_extensions}
    file_extension = Path(file.filename or '').suffix.lower()
    if file_extension not in allowed:
        raise HTTPException(status_code=400, detail=f'Unsupported file type. Allowed types: {", ".join(settings.allowed_extensions)}')

    content = file.file.read()
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(status_code=413, detail='File exceeds the maximum upload size.')

    upload_dir = Path(settings.uploads_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    destination = upload_dir / file.filename
    destination.write_bytes(content)

    try:
        metadata = document_service.ingest_document(destination)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f'Could not process document: {exc}') from exc

    return {'status': 'uploaded', 'document': metadata}


@router.get('/documents')
def list_documents() -> dict:
    return {'documents': document_service.get_documents()}


@router.post('/documents/ingest')
def ingest_documents() -> dict:
    upload_dir = Path(settings.uploads_dir)
    if not upload_dir.exists():
        return {'status': 'ok', 'processed': 0, 'message': 'No documents found to ingest.'}

    ingested = []
    for file_path in sorted(upload_dir.iterdir()):
        if file_path.is_file() and file_path.suffix.lower() in settings.allowed_extensions:
            try:
                metadata = document_service.ingest_document(file_path)
                ingested.append(metadata)
            except Exception:
                continue
    return {'status': 'ok', 'processed': len(ingested), 'documents': ingested}


@router.delete('/documents/{document_id}')
def delete_document(document_id: str) -> dict:
    deleted = document_service.delete_document(document_id)
    if not deleted:
        raise HTTPException(status_code=404, detail='Document not found.')
    return {'status': 'deleted', 'document_id': document_id}
