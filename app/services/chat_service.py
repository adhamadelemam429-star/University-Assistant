from __future__ import annotations

from app.core.retriever import retrieve_relevant_chunks
from app.database.repositories import document_repository
from app.models.schemas import Chunk
from app.rag_pipeline import RAGPipeline


class ChatService:
    def __init__(self):
        self.pipeline = RAGPipeline()
        self.repository = document_repository

    def answer_question(self, question: str) -> dict:
        from app.services.document_service import document_service

        document_service.ensure_sample_documents_ingested()
        chunks = self._load_chunks_from_repository()
        result = self.pipeline.answer_question(question, chunks, llm_enabled=False)
        response = {
            'answer': result.answer,
            'sources': [
                {'document_id': source.document_id, 'file_name': source.file_name, 'page_number': source.page_number}
                for source in result.sources
            ],
        }
        self.repository.add_chat_message({'question': question, 'answer': result.answer})
        return response

    def _load_chunks_from_repository(self) -> list[Chunk]:
        stored_chunks = self.repository.store.list_chunks()
        return [
            Chunk(
                document_id=item.get('document_id', 'unknown'),
                file_name=item.get('file_name', 'unknown'),
                page_number=item.get('page_number'),
                chunk_index=item.get('chunk_index', 0),
                text=item.get('text', ''),
            )
            for item in stored_chunks
        ]


chat_service = ChatService()
