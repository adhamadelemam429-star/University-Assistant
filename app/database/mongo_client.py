from __future__ import annotations

from typing import Any

from app.config import settings


class MongoDBClient:
    def __init__(self):
        self.uri = settings.mongodb_uri
        self.database_name = settings.mongodb_db
        self.client = None
        self.db = None
        self.connected = False

    def connect(self) -> bool:
        if self.connected:
            return True
        try:
            from pymongo import MongoClient
            self.client = MongoClient(self.uri, serverSelectionTimeoutMS=2000)
            self.client.admin.command('ping')
            self.db = self.client[self.database_name]
            self.connected = True
            return True
        except Exception:
            self.client = None
            self.db = None
            self.connected = False
            return False

    def get_database(self) -> Any | None:
        if not self.connected and not self.connect():
            return None
        return self.db


mongo_client = MongoDBClient()
