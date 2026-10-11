from __future__ import annotations

from typing import Any

from app.database.mongo_client import mongo_client


class InMemoryRepository:
    def __init__(self):
        self.documents: dict[str, dict[str, Any]] = {}
        self.chunks: dict[str, dict[str, Any]] = {}
        self.chat_history: list[dict[str, Any]] = []

    def save_document(self, document: dict[str, Any]) -> dict[str, Any]:
        self.documents[document['document_id']] = document
        return document

    def list_documents(self) -> list[dict[str, Any]]:
        return list(self.documents.values())

    def save_chunk(self, chunk: dict[str, Any]) -> dict[str, Any]:
        self.chunks[chunk['chunk_id']] = chunk
        return chunk

    def list_chunks(self) -> list[dict[str, Any]]:
        return list(self.chunks.values())

    def delete_document(self, document_id: str) -> bool:
        if document_id in self.documents:
            del self.documents[document_id]
        self.chunks = {chunk_id: chunk for chunk_id, chunk in self.chunks.items() if chunk.get('document_id') != document_id}
        return True

    def add_chat_message(self, message: dict[str, Any]) -> dict[str, Any]:
        self.chat_history.append(message)
        return message

    def get_chat_history(self) -> list[dict[str, Any]]:
        return list(self.chat_history)


memory_store = InMemoryRepository()


class DocumentRepository:
    def __init__(self):
        self.store = memory_store

    def list_documents(self) -> list[dict[str, Any]]:
        if mongo_client.connect():
            db = mongo_client.get_database()
            if db is not None:
                return list(db.documents.find({}))
        return self.store.list_documents()

    def save_document(self, document: dict[str, Any]) -> dict[str, Any]:
        if mongo_client.connect():
            db = mongo_client.get_database()
            if db is not None:
                db.documents.update_one({'document_id': document['document_id']}, {'$set': document}, upsert=True)
                return document
        return self.store.save_document(document)

    def delete_document(self, document_id: str) -> bool:
        if mongo_client.connect():
            db = mongo_client.get_database()
            if db is not None:
                db.documents.delete_one({'document_id': document_id})
                db.chunks.delete_many({'document_id': document_id})
                return True
        return self.store.delete_document(document_id)

    def save_chunk(self, chunk: dict[str, Any]) -> dict[str, Any]:
        if mongo_client.connect():
            db = mongo_client.get_database()
            if db is not None:
                db.chunks.update_one({'chunk_id': chunk['chunk_id']}, {'$set': chunk}, upsert=True)
                return chunk
        return self.store.save_chunk(chunk)

    def add_chat_message(self, message: dict[str, Any]) -> dict[str, Any]:
        if mongo_client.connect():
            db = mongo_client.get_database()
            if db is not None:
                db.chat_history.insert_one(message)
                return message
        return self.store.add_chat_message(message)


document_repository = DocumentRepository()
